# Main code for Raspberry Pi Model 3B+ -->
#  * Servos and motor control
#  * Camera and light control
#  * Resistor recognition
# ----------------------------------------------------------- #
from globals import *
from utils import *

# ----------------------------------------------------------- #
def run_receiver(rec: Receiver):
    rec.start()

def main():
    camera = Camera()
    motor = Motor(powerSaving=False)
    dispenser = Dispenser()
    plataforma = Plataforma()

    # 0: STOP
    # 1: RUNNING
    # 2: PAUSED
    # 3: EXIT
    is_running = Value('i', 0)  
    # Define the structure of the shared array (list of 5 dictionaries)
    array_size = 5

    # Create a shared array of bytes
    resistances = Array('i', array_size)
    margins = Array('i', array_size)

    receiver = Receiver(port=PORT, ip=IP, is_running=is_running, array_size=array_size, resistances=resistances, margins=margins)
    killer = Killer(is_running=is_running)
    killer.appendObj(camera)
    killer.appendObj(motor)
    killer.appendObj(dispenser)
    killer.appendObj(plataforma)
    killer.appendObj(GPIO)

    if '--no-server' not in sys.argv:
        receiver_process = Process(target=run_receiver, args=(receiver,))
        receiver_process.start()
        killer.appendProc(receiver_process)
    else:
        receiver.is_running.value = 1 # type: ignore
    
    # Loads Recognition models
    cropper = YOLO(yolo_cropper)
    color_bands = YOLO(yolo_segment)

    motor.home()
    camera.start()
    if '--no-renew' not in sys.argv:
        motor.move(100)  # Moves the motor to the position where the screw can be accessed for removal
        plataforma.eject()
    
    started = False
    while receiver.is_running.value != 3: # type: ignore
        while receiver.is_running.value != 1 and receiver.is_running.value != 3: # type: ignore
            sleep(0.1)
        
        if not started:  # Clears terminal window to facilitate reading
            os.system("clear")
            started = True

        for i in range(len(receiver.resistances)):
            motor.storages[i] = [receiver.resistances[i], receiver.margins[i], motor.storages[i][2]]
        print(f"Motor storages: {motor.storages}")

        no_resistor_accum = 0
        while receiver.is_running.value == 1 and no_resistor_accum < 3: # type: ignore
            if '--no-renew' not in sys.argv:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    func1 = executor.submit(dispenser.drop) # Drops ONE resistor onto the platform
                    func2 = executor.submit(motor.shake)  # Shakes the motor while dropping the resistor
                    # Wait for both to complete
                    concurrent.futures.wait([func1, func2])

            sleep(0.5)  # Waits for the resistor to fall onto the platform
            ret, frame = camera.capture()
            ret, frame = camera.capture()
            if not ret:
                for _ in range(3):
                    ret, frame = camera.capture()
                    if ret:
                        break
                    sleep(0.5)
                if not ret:
                    animate_dots("Couldn't retrieve frame from stream", duration=3)
                    raise Exception("Camera Failure.")
            
            oriented = check_orientation(frame)

            Image.fromarray(cv.cvtColor(oriented, cv.COLOR_BGR2RGB)).save(tmp_photo)

            resistor = dict()

            # Runs crop detection model on file
            cropped_infr = cropper(tmp_photo, conf=0.6)
            # Crops and saves original file to a temporary location
            if len(cropped_infr[0].boxes.data):
                print("\033[92m \n\tDetected a resistor\033[0m")
                cropped = cropImage(cv.imread(tmp_photo), cropped_infr[0].boxes.cpu().data[0])
                # Performs white-balancing on image
                balanced = white_balance(cropped)
                Image.fromarray(cv.cvtColor(balanced, cv.COLOR_BGR2RGB)).save(tmp_crop)
                # Runs color bands segmentation model on cropped inference
                colorbands_infr = color_bands(tmp_crop, conf=0.5, iou=0.3)

                try:
                    # Gets masks objects from the inference
                    masks = get_segmentation_masks(tmp_crop, colorbands_infr)
                    # Sorts the masks by distance (it doesn't have a way to 
                    #    know in which direction to start, so by default it 
                    #    uses the leftmost (0,0) point as a beginning.
                    ordered = order_masks(masks, colorbands_infr)

                    for i in range(len(ordered)):
                        color = retrieve_color(cvtBGR2HSV(ordered[i].avgColor))
                        resistor[i] = color
                        print(f"Index: {ordered[i].index} \t HSV: {cvtBGR2HSV(ordered[i].avgColor, paint=True)} \t Predicted: {color}")
                except Exception as e:
                    print(e)

                # Retrieves the resistance value and moves motor accordingly
                ret, resistance = get_resistance(resistor)
                print(f"\033[91m \n\tDetected Resistance: {resistance}\n\033[0m")
                found_slot = motor.find_slot(resistance)
                if not found_slot:
                    print(f"No suitable destination for the resistor...")
                no_resistor_accum = 0
            else:
                # Handles stopping condition when no resistors are 'seen' on image recognition
                no_resistor_accum += 1
                print(f"\033[91m\n\tCouldn't find a resistor, totalling {no_resistor_accum} empty images\n\033[0m")

            if '--no-renew' not in sys.argv:
                plataforma.eject()

    # CLOSING
    motor.move(100)  # Moves the motor to the position where the screw can be accessed for removal
    camera.__del__()
    dispenser.__del__()
    GPIO.__del__()
    if '--no-server' not in sys.argv:
        receiver_process.terminate()


if __name__=="__main__":
    main()