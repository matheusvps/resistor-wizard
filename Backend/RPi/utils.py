# ----------------------------------------------------------- #
from globals import *

# ----------------------------------------------------------- #
# Crops a numpy array image using a bounding box
def cropImage(image, box):
    return image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]


# Performs white balancing on the image
def white_balance(image):
    # Calculate the average color values for each channel
    avg_b = np.mean(image[:, :, 0])
    avg_g = np.mean(image[:, :, 1])
    avg_r = np.mean(image[:, :, 2])

    # Calculate the grey world correction factors
    grey_value = (avg_b + avg_g + avg_r) / 3.0
    scale_b = grey_value / avg_b
    scale_g = grey_value / avg_g
    scale_r = grey_value / avg_r

    # Apply the correction factors to each channel
    balanced_image = image.copy()
    balanced_image[:, :, 0] = np.clip(image[:, :, 0] * scale_b, 0, 255).astype(np.uint8)
    balanced_image[:, :, 1] = np.clip(image[:, :, 1] * scale_g, 0, 255).astype(np.uint8)
    balanced_image[:, :, 2] = np.clip(image[:, :, 2] * scale_r, 0, 255).astype(np.uint8)

    return balanced_image


# Scales all values in an image
def scale_colors(image, scale):
    scale_b, scale_g, scale_r = scale
    # Apply the correction factors to each channel
    scaled_image = image.copy()
    scaled_image[:, :, 0] = np.clip(image[:, :, 0] * scale_b, 0, 255).astype(np.uint8)
    scaled_image[:, :, 1] = np.clip(image[:, :, 1] * scale_g, 0, 255).astype(np.uint8)
    scaled_image[:, :, 2] = np.clip(image[:, :, 2] * scale_r, 0, 255).astype(np.uint8)

    return scaled_image


# Calculates the centroid of a rectangle
def get_centroid(rect):
    cX = (rect[2] + rect[0])/2
    cY = (rect[3] + rect[1])/2
    return (cX, cY)


# Class mask for grouping objects
class Mask:
    def __init__(self, img, bbox = [], contour=[]):
        self.image = img
        self.mask = np.zeros_like(img, dtype=np.uint8)  # creates mask of same size as original image
        self.avgColor = (-1, -1, -1)
        self.bbox = bbox
        self.contour = contour
        self.index = -1  # This color's position relative to others
        self.color = ""  # A string identifier of the color the mask represents
    # Calculates average color on the color band associated with the mask
    def sample_avg_color(self):
        width = int(self.bbox[2] - self.bbox[0])  # Length of edges on X and Y
        height = int(self.bbox[3] - self.bbox[1])
        sX,sY = [int(i) for i in self.bbox[:2]]
        fact = (1 - CENTER_BOX)/2
        summ = np.array([0,0,0])
        nump = 0
        for i in range(sX+CROP_AMOUNT, sX+width-CROP_AMOUNT):
            for j in range(sY+CROP_AMOUNT, sY+height-CROP_AMOUNT):
                if (j < height*fact or j > height*(1 - fact)) and cv.pointPolygonTest(self.contour, (i, j), measureDist=False) == 1:
                    summ += self.image[j][i]
                    nump += 1
        if nump > 0:
            self.avgColor = summ/nump
        else:
            self.avgColor = summ
        
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
    return [a,b]


# Converts BGR color to HSV (0-360, 0-255, 0-255)
def cvtBGR2HSV(bgr, paint: bool=False):
    B,G,R = bgr
    Rp = R/255 
    Gp = G/255 
    Bp = B/255
    Cmax = max(Rp, Gp, Bp)
    Cmin = min(Rp, Gp, Bp)
    delta = Cmax - Cmin
    #
    h = 0
    if delta == 0:
        h = 0
    elif Cmax == Rp:
        h = 60 * (((Gp - Bp) / delta) % 6)
    elif Cmax == Gp:
        h = 60 * (((Bp - Rp) / delta) + 2)
    elif Cmax == Bp:
        h = 60 * (((Rp - Gp) / delta) + 4)
    #
    if Cmax == 0:
        s = 0
    else:
        s = delta/Cmax
    #
    v = Cmax

    if paint:
        s *= 100
        v *= 100
    else:
        s *= 255
        v *= 255
    return [int(i) for i in (h,s,v)]


# Retrieves the pixels contained in the contours given by the model prediction
def get_segmentation_masks(img: str, inference):
    image = cv.imread(img)
    masks = [Mask(image) for _ in range(len(inference[0].masks.xy))]
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
    distances = [-1]*5
    for i in range(len(centroids)-1):
        c1 = np.array(centroids[i])
        c2 = np.array(centroids[i+1])
        distances[i] = np.linalg.norm(c2-c1)
    print(distances)
    if distances.index(max(distances)) == 0:
        ordered.reverse()

    for m in ordered:
        m.index = ordered.index(m)
    return ordered


# Runs and records the execution time of a function
def timer(func, *args, printout: bool=False):
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


# Animates text for exiting the program
def animate_exit(text: str, separator: str="\n"):
    print(text, end=separator)
    for _ in range(3):
        for i in range(1, 4):
            print("Exiting"+i*'.', end="\r")
            sleep(0.5)
            print(" "*len(text), end="")


# Handles user input from terminal call
def handle_input(searchTerm: str, expectedType: type, defaultReturn, fail_msg: str = "Something went wrong when converting types.", exitOnFail: bool = True):
    if searchTerm in sys.argv:     
        try:
            return expectedType(sys.argv[sys.argv.index(searchTerm)+1])
        except:
            if exitOnFail:
                animate_exit()
                exit()
            else:
                print(fail_msg)
    else:
        return defaultReturn


# Compares an HSV value to those stored in a CSV file (min, max per line structure)
def in_range(HSV, file: str):
    score = 0
    minHSV = []
    maxHSV = []
    try:
        with open(file) as f:
            minHSV = [int(i) for i in f.readline().split(',')]
            maxHSV = [int(i) for i in f.readline().split(',')]
        for i in range(3):
            if minHSV[i] <= HSV[i] <= maxHSV[i]:
                score += HSV_weight[i]
    except ValueError:
        score = 0
    return score


# Attempts to find which class an HSV color belongs to
def retrieve_color(hsv):
    H,S,V = hsv
    S /= 2.55
    V /= 2.55  # Converts to Paints' standard to facilitate comparisons
    if (V <= 20 and S <= 50) or (V <= 10) or (180 < H <= 250 and V <= 40):
        return "BLACK"
    if (50 < H <= 250 and 20 < V <= 67 and S <= 25) or (150 < H <= 240 and 20 < V <= 35 and S <= 35):
        return "GREY"
    if (67 < V <= 80 and S <= 20) or (80 < V and S <= 15):
        return "WHITE"
    if (H <= 15 or H >= 310) and S > 60 and V > 30:
        return "RED"
    if (15 < H <= 40 and S > 30 and V > 50) or (15 < H <= 40 and S > 80 and V > 35) or (H < 15 and S < 50 and V > 50):
        return "ORANGE"
    if (40 < H <= 85) and ((H >= 65 and S > 50 and V > 40) or (H < 65 and S > 65 and V > 40)):
        return "YELLOW"
    if (85 < H <= 165 and S > 50 and V > 25):
        return "GREEN"
    if (165 < H <= 245 and S > 50 and V > 20):
        return "BLUE"
    if (245 < H <= 310 and S > 20 and V > 30) or (220 < H <= 245 and 20 < S <= 50 and V > 25):
        return "VIOLET"
    return "BROWN"


# Gets resistance value of resistor from resistance-color table
def get_resistance(resistor: dict):
    if len(resistor) in [3,4]:
        return True, (RESISTANCE_COLOR_VALUES[resistor[0]]*10 + RESISTANCE_COLOR_VALUES[resistor[1]])*(10**RESISTANCE_COLOR_VALUES[resistor[2]])
    elif len(resistor) == 5:
        return True, (RESISTANCE_COLOR_VALUES[resistor[0]]*100 + RESISTANCE_COLOR_VALUES[resistor[1]]*10 + RESISTANCE_COLOR_VALUES[resistor[2]])*(10**RESISTANCE_COLOR_VALUES[resistor[3]])
    else:
        return False, -1


class Motor:
    def __init__(self, stepPin: int=Passo_SM, dirPin: int=Direcao_SM, sleepPin: int=Sleep_SM, stepsPerRev: int=stepsPerRevolution, minDt: float=minDeltaT, hallFXPIN: int=Hall_effect, powerSaving: bool=True, logging: bool=False):
        self.stepPin = stepPin
        self.dirPin = dirPin
        self.sleepPin = sleepPin
        self.stepsPerRev = stepsPerRev
        self.minDt = minDt
        self.hall_pin = hallFXPIN
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
        self.power_save = powerSaving
        self.storages = {  # index: [resistance, margin, position]
            0:[-1,-1,0], 
            1:[-1,-1,33], 
            2:[-1,-1,67], 
            3:[-1,-1,100], 
            4:[-1,-1,133], 
        }
        #
        self.Sleep()
    # Puts Motor driver on SLEEP mode
    def Sleep(self, state: bool=True):
        if self.power_save == False:
            GPIO.output(self.sleepPin, GPIO.HIGH)
            return
        if state == True:
            GPIO.output(self.sleepPin, GPIO.LOW)
        else:
            GPIO.output(self.sleepPin, GPIO.HIGH)
    # Homes Motor position
    def home(self):
        self.Sleep(False)
        self.setDirection(0)
        while GPIO.input(self.hall_pin) == GPIO.HIGH:  # While Hall doesn't detect magnet, step motor
            self.step()
            sleep(0.01)
        self.invertDirection()
        self.step()
        sleep(1)
        self.position = 100  # Default home positon (arbitrary)
        self.Sleep(True)
    # Updates Motors stats
    def update(self, safe_mode: bool=True):
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
    def formatRatio(self, b: float, a: float):
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
        for i in range(numSteps):
            if i < int(self.accel_steps * self.formatRatio(numSteps, 2*self.accel_steps)):
                self.speed += self.accel * self.formatRatio(numSteps, 2*self.accel_steps)
            elif numSteps - int(self.accel_steps * self.formatRatio(numSteps, 2*self.accel_steps)) <= i:
                self.speed -= self.accel * self.formatRatio(numSteps, 2*self.accel_steps)
            self.step()
            self.update()
            sleep(self.tDelay)
        self.Sleep(True)
    # "Shakes" the motor as to decrease odds of dispenser failing
    def shake(self):
        self.Sleep(False)
        numSteps = 12 # 21,6deg (change according to need)
        freq = 200 # Hz
        period = 1/freq
        for _ in range(numSteps):
            self.step()
            self.update()
            sleep(period)
        self.invertDirection()  # Inverts the direction of rotation
        for _ in range(numSteps):
            self.step()
            self.update()
            sleep(period)
        self.invertDirection()  # Inverts the direction of rotation
        self.Sleep(True)
    # Finds which storage a resistor must go into and moves the motor to it
    def find_slot(self, resistance: int):
        for slot in self.storages.values():
            if slot[0] == -1:
                continue
            if slot[0] - slot[1] <= resistance <= slot[0] + slot[1]:
                self.move(slot[2])
                return True
        self.move(167)
        return False


class Dispenser:
    def __init__(self, togglePin: int=ToggleServo, topBladePin: int=Servo_Dispenser_Cima, bottomBladePin: int=Servo_Dispenser_Baixo, logging: bool=False):
        self.topBlade = GPIO.PWM(topBladePin, 50)
        self.bottomBlade =  GPIO.PWM(bottomBladePin, 50)
        self.power_state = False
        self.power_pin = togglePin
        self.logger = logging
        #
        self.topBlade.start(0)
        self.bottomBlade.start(0)
    # Defines Power state for ALL(!!) Servos
    def Power(self, state: bool=True):
        if self.power_state != state:
            self.power_state = state
            GPIO.output(self.power_pin, (lambda x: GPIO.LOW if x == False else GPIO.HIGH)(state))
    # Function that vibrates the servos so as to makes the resistors fall
    def vibrate(self, duration=1): # Duration in seconds
        startState = self.power_state
        self.Power()
        sleep(0.1)
        self.topBlade.ChangeDutyCycle(10.2)
        start = time()
        while time() - start < duration:
            self.topBlade.ChangeDutyCycle(10.7)
            sleep(0.05)
            self.topBlade.ChangeDutyCycle(10.1)
            sleep(0.05)
        self.Power(startState)
    # Sequence to drop a single resistor
    def drop(self):
        delay = 0.3
        self.Power()
        sleep(0.05)
        self.topBlade.ChangeDutyCycle(11.5) # Top Closes
        self.bottomBlade.ChangeDutyCycle(2) # Bottom Closes
        sleep(delay)
        self.topBlade.ChangeDutyCycle(10.2) # Top Opens
        self.vibrate()
        sleep(delay)
        self.topBlade.ChangeDutyCycle(11.5) # Top Closes
        sleep(delay)
        self.bottomBlade.ChangeDutyCycle(3) # Bottom Opens
        sleep(delay)
        self.bottomBlade.ChangeDutyCycle(2) # Bottom closes
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
    def __init__(self, index: int=CAMERA_INDEX, focus: int=CAMERA_FOCUS, exposure: int=CAMERA_EXPOSURE, toggleLED: int=ToggleLED, LEDState: bool = True):
        self.index = index
        self.focus = focus
        self.exposure = exposure
        self.powerLED = toggleLED
        self.LEDState = LEDState
        self.primed = False
        # Sets camera's capture properties
        self.dev = cv.VideoCapture(self.index)
        while not self.dev.isOpened():
            self.index += 1
            self.dev = cv.VideoCapture(self.index)
        self.dev.read()
        self.dev.set(cv.CAP_PROP_BUFFERSIZE, 1)
        self.dev.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
        self.dev.set(cv.CAP_PROP_AUTOFOCUS, 0)
        self.dev.set(cv.CAP_PROP_EXPOSURE, self.exposure)
        self.dev.set(cv.CAP_PROP_FOCUS, self.focus)
        self.dev.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
        self.dev.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    # Toggles LED state
    def Flash(self, state=True):
        if self.LEDState == True:
            GPIO.output(self.powerLED, state)
        else:
            GPIO.output(self.powerLED, False)
            
    #  Starts camera and adjusts exposure 
    def start(self):
        if self.primed:
            return
        self.Flash()
        for _ in range(5):  # Reads 5 images to prime the input
            _, _ = self.dev.read()
        self.primed = True
        self.Flash(False)
    # Captures image from camera
    def capture(self):
        self.Flash()
        sleep(0.1)
        img = self.dev.read()
        sleep(0.1)
        self.Flash(False)
        return img
    # Class destroyer
    def __del__(self):
        self.dev.release()
        cv.destroyAllWindows()


class Plataforma:
    def __init__(self, togglePin: int=ToggleServo, platPin: int=Servo_Plataforma, logging: bool=False):
        self.control = GPIO.PWM(platPin, 50)
        self.power_state = False
        self.power_pin = togglePin
        self.logger = logging
        #
        self.control.start(0)
    # Defines Power state for ALL(!!) Servos
    def Power(self, state: bool=True):
        if self.power_state != state:
            self.power_state = state
            GPIO.output(self.power_pin, (lambda x: GPIO.LOW if x == False else GPIO.HIGH)(state)) 
    # Ejects the resistor from the platform
    def eject(self):
        self.Power()
        sleep(0.05)
        delay = 0.005
        for i in range(23, 71):
            dc = i/10
            self.control.ChangeDutyCycle(dc)
            sleep(delay)
        for i in range(70, 22, -1):
            dc = i/10
            self.control.ChangeDutyCycle(dc)
            sleep(delay)
        self.Power(False)


class Receiver:
    def __init__(self, port: int, ip: str, is_running, array_size: int, resistances, margins):
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
            self.is_running.value = True # type: ignore
            resistances = request.json
            self.update_array(self.resistances, [res["resistance"] for res in resistances])
            self.update_array(self.margins, [res["margin"] for res in resistances])
            print(resistances)
            return jsonify({"message": "Data received successfully"})

        @self.app.route("/api/stop", methods=['OPTIONS', 'POST'])
        @cross_origin(supports_credentials=True)    
        def stop():
            self.is_running.value = False # type: ignore
            return 'OK'

    def update_array(self, target, values):
        for i in range(min(self.arrSize, len(values))):
            try:
                target[i] = int(values[i])
            except ValueError:
                continue

    def start(self):
        self.app.run(host=self.ip, port=self.port)
    





