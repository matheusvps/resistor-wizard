from utils import *

WORKINGDIR = os.path.dirname(os.path.abspath( __file__ ))

def main():    
    SAVEDIR = handle_input('--savedir', str, os.path.join(WORKINGDIR, "csv"), "Problem setting saving directory path from input.")
        
    if not os.path.isdir(SAVEDIR):
        os.mkdir(SAVEDIR)

    crop = handle_input('--crop', bool, False)
    cropper = None
    if crop:
        cropper = YOLO("LATEST/cropper.pt")
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    camera = Camera()
    dispenser = Dispenser()
    platforma = Plataforma()

    if '--no-renew' not in sys.argv:
        platforma.eject()
        dispenser.drop()

    # No more than 30 can possibly fit inside the dispenser so it's safe to use it
    numImages = handle_input('--num-images', int, 30, "Problem acquiring number of training images from input.")

    photos_processed = 0
    while photos_processed < numImages:
        _, frame = camera.capture()
        if crop:
            Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB)).save(tmp_photo)
            cropped_infr = cropper(tmp_photo, conf=0.6)
            cropped = cropImage(cv.imread(tmp_photo), cropped_infr[0].boxes.cpu().data[0])
            # Performs white-balancing on image
            balanced = white_balance(cropped)
            Image.fromarray(cv.cvtColor(balanced, cv.COLOR_BGR2RGB)).save(os.path.join(SAVEDIR, f"cropped_{photos_processed}.png"))
        else:
            Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB)).save(os.path.join(SAVEDIR, f"photo_{photos_processed}.png"))

        photos_processed += 1



if __name__=="__main__":
    main()