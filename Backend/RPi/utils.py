# ----------------------------------------------------------- #
from globals import *

# ----------------------------------------------------------- #
# Crops a numpy array image using a bounding box
def cropImage(image, box):
    return image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]


# Calculates the centroid of a rectangle
def get_centroid(rect):
    cX = (rect[2] + rect[0])/2
    cY = (rect[3] + rect[1])/2
    return (cX, cY)


# Checks if two colors are equal
def eqq(a,b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
                return False
    return True

# Calculates the equivalent vector sum of two vectors/colors
def vec_sum(v1, v2):
    if len(v1) != len(v2):
        raise Exception("Lengths of vectors passed are not the same")
    out = [0]*len(v1)
    for i in range(len(v1)):
        out[i] = v1[i] + v2[i]
    return out

# Class mask for grouping objects
class Mask:
    def __init__(self, img, bbox=[], contour=[]):
        self.image = img
        self.mask = np.zeros_like(img, dtype=np.uint8)  # creates mask of same size as original image
        self.avgColor = (None, None, None)
        self.bbox = bbox
        self.contour = contour
        self.index = -1  # This color's position relative to others
        self.color = ""  # A string identifier of the color the mask represents
    # Calculates average color on the color band associated with the mask
    def sample_avg_color(self):
        center = [int(j) for j in get_centroid([float(i) for i in self.bbox[:4]])]  # Center of Bounding box
        xLength = self.bbox[2] - self.bbox[0]  # Length of edges on X and Y
        yLength = self.bbox[3] - self.bbox[1]
        sX = int(center[0] - ((SCALE_BBOX*xLength)/2))  # Top left corner of box to consider for averaging
        sY = int(center[1] - ((SCALE_BBOX*yLength)/2))
        eX = int(sX + (SCALE_BBOX*xLength))
        eY = int(sY + (SCALE_BBOX*yLength))
        summ = np.array([0,0,0])
        nump = 0
        for i in range(sX, eX+1):
            for j in range(sY, eY+1):
                if cv.pointPolygonTest(self.contour, (i, j), measureDist=False) == 1:
                    summ += self.image[j][i]
                    nump += 1
        self.avgColor = summ/nump
        
    # Checks if a point is inside the mask's bounding box
    def contains(self, point):
        if list(point) < self.bbox[0:2].tolist() or list(point) > self.bbox[2:4].tolist():
            return False
        else:
            return True


# Calculates the linear regression of the points in a 2D dataset: Y in function of X (Y= a*X + b)
def lin_reg(data):
    X = np.array([i[0] for i in data])
    Y = np.array([i[1] for i in data])
    a = ((len(data) * np.sum(X*Y)) - (np.sum(X) * np.sum(Y)))/(len(data) * np.sum(X*X) - (np.sum(X))**2)
    b = ((np.sum(Y) * np.sum(X*X)) - (np.sum(X) * np.sum(X*Y)))/(len(data) * np.sum(X*X) - (np.sum(X))**2)
    return a,b


# Converts BGR color to HSV (0-360, 0-255, 0-255)
def cvtBGR2HSV(bgr, paint=False):
    B,G,R = bgr
    Rp = R/255 
    Gp = G/255 
    Bp = B/255
    Cmax = max(Rp, Gp, Bp)
    Cmin = min(Rp, Gp, Bp)
    delta = Cmax - Cmin
    #
    if delta == 0:
        H = 0
    elif Cmax == Rp:
        H = 60 * (((Gp - Bp) / delta) % 6)
    elif Cmax == Gp:
        H = 60 * (((Bp - Rp) / delta) + 2)
    elif Cmax == Bp:
        H = 60 * (((Rp - Gp) / delta) + 4)
    #
    if Cmax == 0:
        S = 0
    else:
        S = delta/Cmax
    #
    V = Cmax

    if paint:
        S *= 100
        V *= 100
    else:
        S *= 255
        V *= 255
    return [int(i) for i in (H,S,V)]


# Retrieves the pixels contained in the contours given by the model prediction
def get_segmentation_masks(img, inference, data=255):
    image = cv.imread(img)
    masks = [Mask(image) for i in range(len(inference[0].masks.xy))]
    for i in range(len(inference[0].masks.xy)):
        polygon = inference[0].masks.xy[i].astype(int)
        masks[i].contour = polygon
        masks[i].bbox = inference[0].boxes.cpu().data[i]
        masks[i].sample_avg_color()
    return masks


# Finds the mask that contains a given point – considers a point can belong to a single mask
def retrieve_point_in_mask(masks, point):
    for mask in masks:
        if mask.contains(point):
            return mask


# Calculates the possible orders of the color bands – assumes the bands are approximately
#     linear, which is reasonable given that resistors follow this standard
def order_masks(masks, inference):
    boxes = inference[0].boxes.cpu().data
    vertex = [v[:4] for v in boxes]
    centroids = [get_centroid(v) for v in vertex]
    #
    # Calculates the line that approximately crosses the centroids – it's used to find the order in which the bands are disposed
    parameters = lin_reg(centroids)
    lv = np.array([1,parameters[0]]) # Line Vector
    lv_norm = np.sqrt(sum(lv**2))
    #
    vects = {}
    for center in centroids:
        u = np.array(center) - np.array([0,parameters[1]])  # Calculates the vector from the origin of the line to the centroid
        proj = lv * np.dot(u,lv) / (lv_norm**2)  # Projects the centroid onto the line
        vects[retrieve_point_in_mask(masks, center)] = np.sqrt(np.sum(proj**2))  # Calculates each centroid's distance to origin and associates it to its respective mask
    # Sorts masks by distance
    sorted_masks = dict(sorted(vects.items(), key=lambda item: item[1]))

    #if len(sorted_masks) != len(masks):
    #  ~ TERMINAR CODIGO DE ROTAÇÃO DAS IMAGENS CASO ESTEJA VERTICAL... ~

    ordered = list(sorted_masks)
    for m in ordered:
        m.index = ordered.index(m)
    return ordered


# Runs and records the execution time of a function
def timer(func, *args, printout=False):
    """
        Times the execution of a function\n
        Arguments:\n
            func: function to be timed\n
            *args: occasional arguments to be passed to the function called\n
            printout: wheter to print to console or not\n
        Output:\n
            res: the output from the function ran\n
            dt = time elapsed since beginning and end of the function\n
    """
    start = time()
    res = func(*args)
    end = time()
    dt = end - start
    if printout:
        print(f"Function \033[94m {func.__name__} \033[0m took {dt:.{2}f}s to run.")
    return res, dt


class Motor:
    def __init__(self, stepPin=Passo_SM, dirPin=Direcao_SM, sleepPin=Sleep_SM, stepsPerRev=stepsPerRevolution, minDt=minDeltaT, logging=False):
        self.stepPin = stepPin
        self.dirPin = dirPin
        self.sleepPin = sleepPin
        self.stepsPerRev = stepsPerRev
        self.minDt = minDt
        self.position = 0  # Position measured in steps (0 is at startup, before homing)
        self.direction = 1 # 1 for HIGH on dirPin, 0 for LOW
        self.speed = 50  # Steps per sec
        self.min_speed = 50
        self.max_speed = 350
        self.accel = 5  # Acceleration in frequency change per sec
        self.tDelay = 0  # Calculated based on self.speed
        self.max_move_time = 2 # Max time duration in seconds of any movement (while keeping speed under max_speed)
        self.accel_steps = int((self.max_speed-self.min_speed)/self.accel)
        self.logger = logging
    # Puts Motor driver on SLEEP mode
    def Sleep(self, state=True):
        if state == True:
            GPIO.output(self.sleepPin, GPIO.LOW)
        else:
            GPIO.output(self.sleepPin, GPIO.HIGH)
    # Updates Motors stats
    def update(self, safe_mode=True):
        if safe_mode and self.speed > self.max_speed:
            self.speed = self.max_speed
        elif safe_mode and self.speed < self.min_speed:
            self.speed = self.min_speed
        self.position %= self.stepsPerRev
        self.tDelay = (1/self.speed) - 2*minDeltaT
        # Logging
        if self.logger == True:
            print(f"Position: {self.position}\t Direction: {self.direction}\t Speed: {int(self.speed)}\t Delay: {self.tDelay:.4f}")
    # Sends a step signal to the Stepper Motor
    def step(self):
        GPIO.output(self.stepPin, GPIO.HIGH)
        sleep(self.minDt)
        GPIO.output(self.stepPin, GPIO.LOW)
        sleep(self.minDt)
        if self.direction == 1:
            self.position += 1
        else:
            self.position -= 1
    # Inverts direction of the motor rotation
    def invertDirection(self):
        GPIO.output(self.dirPin, not GPIO.input(self.dirPin))
        self.direction = int(not self.direction)  # Toggles direction
    # Stes the direction of rotation of the motor
    def setDirection(self, dir: int):
        GPIO.output(self.dirPin, bool(dir))
        self.direction = dir
    # Formats the ratio of variables to [0-1]
    def formatRatio(self, b, a):
        if b>a:
            return 1
        return b/a
    # Rotates the motor "pos" steps
    def move(self, pos: int):  # Position given in STEPS!
        self.Sleep(False)
        #pos %= self.stepsPerRev
        if (pos - self.position) < 0:
            self.setDirection(0)
        else:
            self.setDirection(1)
        numSteps = abs(self.position - pos)
        for i in range(numSteps+1):
            if i < int(self.accel_steps * self.formatRatio(numSteps, 2*self.accel_steps)):
                self.speed += self.accel * self.formatRatio(numSteps, 2*self.accel_steps)
            elif numSteps - int(self.accel_steps * self.formatRatio(numSteps, 2*self.accel_steps)) <= i:
                self.speed -= self.accel * self.formatRatio(numSteps, 2*self.accel_steps)
            self.update()
            self.step()
            sleep(self.tDelay)
        self.Sleep(True)

class Dispenser:
    def __init__(self, togglePin=ToggleServo, topBladePin=Servo_Dispenser_Cima, bottomBladePin=Servo_Dispenser_Baixo, logging=False):
        self.topBlade = GPIO.PWM(topBladePin, 50)
        self.bottomBlade =  GPIO.PWM(bottomBladePin, 50)
        self.power_state = False
        self.power_pin = togglePin
        self.logger = logging
        #
        self.topBlade.start(0)
        self.bottomBlade.start(0)
    # Defines Power state for ALL(!!) Servos
    def Power(self, state=True):
        if self.power_state != state:
            self.power_state = state
            GPIO.output(self.power_pin, (lambda x: GPIO.LOW if x == False else GPIO.HIGH)(state))
    # Function that vibrates the servos so as to makes the resistors fall
    def vibrate():
        pass
    # Sequence to drop a single resistor
    def drop(self):
        delay = 0.3
        self.Power()
        sleep(0.05)
        self.topBlade.ChangeDutyCycle(11.5)
        self.bottomBlade.ChangeDutyCycle(2)
        sleep(delay)
        self.topBlade.ChangeDutyCycle(10)
        sleep(delay)
        self.topBlade.ChangeDutyCycle(11.5)
        sleep(delay)
        self.bottomBlade.ChangeDutyCycle(3)
        sleep(delay)
        self.bottomBlade.ChangeDutyCycle(2)
        sleep(delay)
        self.Power(False)
        
    def __del__(self):
        self.topBlade.stop()
        self.bottomBlade.stop()
        self.Power(state=False)

class CustomError(Exception):
    """Custom error class."""
    pass

class Camera:
    def __init__(self, index=CAMERA_INDEX, focus=CAMERA_FOCUS, exposure=CAMERA_EXPOSURE, toggleLED=ToggleLED):
        self.index = index
        self.focus = focus
        self.exposure = exposure
        self.powerLED = toggleLED
        self.primed = False
        # Sets camera's capture properties
        self.dev = cv.VideoCapture(self.index)
        self.dev.set(cv.CAP_PROP_BUFFERSIZE, 1)
        self.dev.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.dev.set(cv.CAP_PROP_EXPOSURE, self.exposure)
        self.dev.set(cv.CAP_PROP_FOCUS, self.focus)
        self.dev.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        self.dev.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    #  Starts camera and adjusts exposure 
    def start(self):
        if self.primed:
            return
        GPIO.output(self.powerLED, GPIO.HIGH)
        for i in range(5):  # Reads 5 images to prime the input
            _, _ = self.dev.read()
        self.primed = True
        GPIO.output(self.powerLED, GPIO.LOW)
    # Captures image from camera
    def capture(self):
        GPIO.output(self.powerLED, GPIO.HIGH)
        sleep(0.1)
        img = self.dev.read()
        sleep(0.1)
        GPIO.output(self.powerLED, GPIO.LOW)
        return img
    # Class destroyer
    def __del__(self):
        self.dev.release()
        cv.destroyAllWindows()

class Plataforma:
    def __init__(self, togglePin=ToggleServo, platPin=Servo_Plataforma, logging=False):
        self.control = GPIO.PWM(platPin, 50)
        self.power_state = False
        self.power_pin = togglePin
        self.logger = logging
        #
        self.control.start(0)
    # Defines Power state for ALL(!!) Servos
    def Power(self, state=True):
        if self.power_state != state:
            self.power_state = state
            GPIO.output(self.power_pin, (lambda x: GPIO.LOW if x == False else GPIO.HIGH)(state)) 
    # Ejects the resistor from the platform
    def eject(self):
        delay = 0.3
        self.Power()
        sleep(0.05)
        self.control.ChangeDutyCycle(2.3)
        sleep(delay)
        self.control.ChangeDutyCycle(7)
        sleep(delay)
        self.control.ChangeDutyCycle(2.3)
        sleep(delay)
        self.Power(False)

class Receiver:
    def __init__(self, port, ip, is_running, array_size, resistances, margins):
        self.port = port
        self.ip = ip
        self.is_running = is_running
        self.arrSize = array_size
        self.resistances = resistances  #
        self.margins = margins          #
        self.app = Flask(__name__)
        CORS(self.app, supports_credentials=True)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        
        # Set up routes dynamically based on instance attributes
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/api/send_resistances', methods=['OPTIONS', 'POST'])
        @cross_origin(supports_credentials=True)
        def receive_resistances():
            self.is_running.value = True
            resistances = request.json
            self.update_array(self.resistances, [res["resistance"] for res in resistances])
            self.update_array(self.margins, [res["margin"] for res in resistances])
            print(resistances)
            return jsonify({"message": "Data received successfully"})

        @self.app.route("/api/stop", methods=['OPTIONS', 'POST'])
        @cross_origin(supports_credentials=True)    
        def stop():
            self.is_running.value = False
            return 'OK'

    def update_array(self, target, values):
        for i in range(min(self.arrSize, len(values))):
            try:
                target[i] = int(values[i])
            except ValueError:
                continue

    def start(self):
        self.app.run(host=self.ip, port=self.port)
    





