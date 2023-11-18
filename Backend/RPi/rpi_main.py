# Main code for Raspberry Pi Model 3B+ -->
#  * Servos and motor control
#  * Camera and light control
#  * Resistor recognition
# ----------------------------------------------------------- #
from globals import *
from utils import *

# ----------------------------------------------------------- #
def run_receiver(rec):
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

    receiver_process = Process(target=run_receiver, args=(receiver,))
    receiver_process.start()
    
    # Loads Recognition models
    cropper = YOLO("../LATEST/cropper.pt")
    color_bands = YOLO("../LATEST/segmenter.pt")

    motor.Sleep()
    camera.start()
    if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
        plataforma.eject()
    
    while not receiver.is_running.value:
        sleep(0.1)

    while receiver.is_running.value:        
        #start = time()
        # Check for user input to adjust exposure and focus
        
        if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
            dispenser.drop()  # Drops ONE resistor onto the platform
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
        Image.fromarray(cv.cvtColor(cropped, cv.COLOR_BGR2RGB)).save(tmp_crop)


        # Runs color bands segmentation model on cropped inference
        if len(cropped_infr[0].boxes.data):
            colorbands_infr = color_bands(tmp_crop, conf=0.6, iou=0.3)
        else:
            colorbands_infr = color_bands(tmp_photo, conf=0.6, iou=0.3)


        try:
            # Gets masks objects from the inference
            masks, _ = timer(get_segmentation_masks, tmp_crop, colorbands_infr, printout=True)
            # Sorts the masks by distance (it doesn't have a way to 
            #    know in which direction to start, so by default it 
            #    uses the leftmost (0,0) point as a beginning.
            ordered, _ = timer(order_masks, masks, colorbands_infr, printout=True)
        
            for i in range(len(ordered)):
                print(f"BBOX: {[int(j) for j in ordered[i].bbox[:4]]} \t Index: {ordered[i].index} \t HSV: {cvtBGR2HSV(ordered[i].avgColor, paint=True)}")
        except Exception as e:
            print(e)

        if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
            plataforma.eject()

        # This needs to be the LAST line on the loop
        # if time() - start < (1/MAX_IPS):  # If execution rate is faster than MAX_IPS, wait so as to not overload the processor
        #     sleep((1/MAX_IPS) - time())



    # CLOSING
    camera.__del__()
    dispenser.__del__()
    GPIO.cleanup()
    receiver_process.terminate()


if __name__=="__main__":
    main()