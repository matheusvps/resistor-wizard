# Main code for Raspberry Pi Model 3B+ -->
#  * Servos and motor control
#  * Camera and light control
#  * Resistor recognition
# ----------------------------------------------------------- #
from globals import *
from utils import *
from PIL import ImageDraw

# ----------------------------------------------------------- #


def main():
    camera = Camera()
    motor = Motor()
    dispenser = Dispenser()
    plataforma = Plataforma()

    # Loads Recognition models
    cropper = YOLO("LATEST/cropper.pt")
    color_bands = YOLO("LATEST/color_band_segment_grayscale_v13.pt")

    motor.home()
    camera.start()
    if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
        plataforma.eject()

    no_resistor_accum = 0
    while no_resistor_accum < 3:
        resistor_exists = True       
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
            balanced = white_balance(cropped)
            Image.fromarray(cv.cvtColor(cropped, cv.COLOR_BGR2RGB)).save("tmp/unbalanced.png")
            Image.fromarray(cv.cvtColor(balanced, cv.COLOR_BGR2RGB)).save(tmp_crop)
            # Runs color bands segmentation model on cropped inference
            colorbands_infr = color_bands(tmp_crop, conf=0.6, iou=0.3)
            try:
                # Gets masks objects from the inference
                masks, _ = timer(get_segmentation_masks, tmp_crop, colorbands_infr, printout=True)
                # Sorts the masks by distance (it doesn't have a way to 
                #    know in which direction to start, so by default it 
                #    uses the leftmost (0,0) point as a beginning.
                ordered, _ = timer(order_masks, masks, colorbands_infr, printout=True)

                labeled = Image.open(tmp_crop)
                for i in range(len(ordered)):
                    ImageDraw.Draw(labeled).text((ordered[i].bbox[0], ordered[i].bbox[1]), str(i), fill=(255,0,0))
                labeled.save(os.path.join(tmp_dir, "labeled.png"))
                print(f"\n\n\tLABELS SAVED, PLEASE run 'SCP' FROM \n\tHOST MACHINE TO GET THE UPDATED \n\tIMAGE.\n\n")

                for i in range(len(ordered)):
                    print(f"Index: {ordered[i].index} \t HSV: {cvtBGR2HSV(ordered[i].avgColor, paint=True)}, {cvtBGR2HSV(ordered[i].avgColor)} \t Predicted: {retrieve_color(cvtBGR2HSV(ordered[i].avgColor)).upper()}")
                input()

            except Exception as e:
                if e == AttributeError:
                    print(e)
                    resistor_exists = False
                    print("Couldn't detect color bands...")
                

        # Handles stopping condition when no resistors are seen based on image recognition
        if resistor_exists:
            no_resistor_accum = 0
        else:
            no_resistor_accum += 1
                
        if len(sys.argv) == 1 or sys.argv[1] != '--no-renew':
            plataforma.eject()



    # CLOSING
    camera.__del__()
    dispenser.__del__()
    GPIO.cleanup()


if __name__=="__main__":
    main()
    os.remove(TMPCSV)