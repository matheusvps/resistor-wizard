# Main code for Raspberry Pi Model 3B+ -->
#  * Servos and motor control
#  * Camera and light control
#  * Resistor recognition
# ----------------------------------------------------------- #
from globals import *
from utils import *

# ----------------------------------------------------------- #

def main():
    camera = Camera()
    motor = Motor()
    dispenser = Dispenser()
    
    while True:  # ~ CHANGE CONDITION TO WHILE SERVER IS ON OR CAMERA RECOGNIZES RESISTORS ~
        start = time()  
        ret, frame = camera.capture()
        if not ret:
            raise Exception("Couldn't retrieve frame from stream.")
            exit()
        
        if time() - start < (1/MAX_IPS):  # If execution rate is faster than MAX_IPS, wait so as to not overload the processor
            sleep((1/MAX_IPS) - time())


if __name__=="__main__":
    mot = Motor(logging=True)
    mot.move(600)