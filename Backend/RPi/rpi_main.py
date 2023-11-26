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
    motor = Motor()
    dispenser = Dispenser()
    plataforma = Plataforma()

    is_running = Value('i', False)
    # Define the structure of the shared array (list of 5 dictionaries)
    array_size = 5

    # Create a shared array of bytes
    resistances = Array('i', array_size)
    margins = Array('i', array_size)

    receiver = Receiver(port=PORT, ip=IP, is_running=is_running, array_size=array_size, resistances=resistances, margins=margins)

    if len(sys.argv) == 1 or '--no-server' not in sys.argv:
        receiver_process = Process(target=run_receiver, args=(receiver,))
        receiver_process.start()
    else:
        receiver.is_running.value = True
    
    # Loads Recognition models
    cropper = YOLO("LATEST/cropper.pt")
    color_bands = YOLO("LATEST/color_band_segment_grayscale.pt")

    motor.home()
    camera.start()
    if len(sys.argv) == 1 or '--no-renew' not in sys.argv:
        plataforma.eject()
    
    
    while not receiver.is_running.value: # type: ignore
        sleep(0.1)

    for i in range(len(receiver.resistances)):
        motor.storages[i] = [receiver.resistances[i], receiver.margins[i]]

    no_resistor_accum = 0
    while receiver.is_running.value and no_resistor_accum < 3: # type: ignore
        resistor_exists = True       
        if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
            with concurrent.futures.ThreadPoolExecutor() as executor:
                func1 = executor.submit(dispenser.drop) # Drops ONE resistor onto the platform
                func2 = executor.submit(motor.shake)  # Shakes the motor while dropping the resistor
                # Wait for both to complete
                concurrent.futures.wait([func1, func2])
            
        sleep(0.3)  # Waits for the resistor to fall onto the platform
        ret, frame = camera.capture()
        ret, frame = camera.capture()
        if not ret:
            for _ in range(3):
                ret, frame = camera.capture()
                if ret:
                    break
                sleep(0.5)
            if not ret:
                raise Exception("Couldn't retrieve frame from stream.")
                exit()

        
        Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB)).save(tmp_photo)

        # Runs crop detection model on file
        cropped_infr = cropper(tmp_photo, conf=0.6) 
        # Crops and saves original file to a temporary location
        if len(cropped_infr[0].boxes.data):
            cropped = cropImage(cv.imread(tmp_photo), cropped_infr[0].boxes.cpu().data[0])
        else:
            cropped = cv.imread(tmp_photo)
            resistor_exists = False
        Image.fromarray(cv.cvtColor(cropped, cv.COLOR_BGR2RGB)).save(tmp_crop)


        # Runs color bands segmentation model on cropped inference
        if len(cropped_infr[0].boxes.data):
            colorbands_infr = color_bands(tmp_crop, conf=0.6, iou=0.3)
        else:
            colorbands_infr = color_bands(tmp_photo, conf=0.6, iou=0.3)


        resistor = dict()

        try:
            # Gets masks objects from the inference
            masks, _ = timer(get_segmentation_masks, tmp_crop, colorbands_infr, printout=True)
            # Sorts the masks by distance (it doesn't have a way to 
            #    know in which direction to start, so by default it 
            #    uses the leftmost (0,0) point as a beginning.
            ordered, _ = timer(order_masks, masks, colorbands_infr, printout=True)
            if len(ordered) == 0:
                resistor_exists = False
            for i in range(len(ordered)):
                color, _ = timer(retrieve_color(cvtBGR2HSV(ordered[i].avgColor)), printout=True)
                resistor[i] = color
        except Exception as e:
            print(e)

        # Retrieves the resistance value and moves motor accordingly
        ret, resistance = get_resistance(resistor)
        found_slot = motor.find_slot(resistance)
        if not found_slot:
            print(f"Couldn't find a suitable slot for the resistor...")

        # Handles stopping condition when no resistors are left based on image recognition
        if not resistor_exists:
            no_resistor_accum += 1
            print(f"\n\tCouldn't find a resistor in the image, at a total of {no_resistor_accum} empty images\n")
        else:
            no_resistor_accum = 0

        if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
            plataforma.eject()


    # CLOSING
    camera.__del__()
    dispenser.__del__()
    GPIO.cleanup()
    if len(sys.argv) == 1 or '--no-server' not in sys.argv:
        receiver_process.terminate()


if __name__=="__main__":
    main()