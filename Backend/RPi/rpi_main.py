# Main code for Raspberry Pi Model 3B+ -->
#  * Servos and motor control
#  * Camera and light control
#  * Resistor recognition
# ----------------------------------------------------------- #
from globals import *

# ----------------------------------------------------------- #

def main():
    cap = cv.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise Exception("Couldn't open camera feed.")
        exit()
    
    while True:  # ~ CHANGE CONDITION TO WHILE SERVER IS ON OR CAMERA RECOGNIZES RESISTORS ~
        start = time()  
        ret, frame = cap.read()

        if not ret:
            raise Exception("Couldn't retrieve frame from stream.")
            exit()
        
        if time() - start < (1/MAX_IPS):  # If execution rate is faster than MAX_IPS, wait so as to not overload the processor
            sleep((1/MAX_IPS) - time())


        
    

if __name__=="__main__":
    main()