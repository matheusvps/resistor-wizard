# ----------------------  IMPORTS  -------------------------- #
from utils import *  # Other global parameters are defined here
from ultralytics import YOLO
from PIL import Image
import csv
import numpy as np
import cv2 as cv
from time import time, sleep
import os

import RPi.GPIO as GPIO

# ----------------------------------------------------------- #



CROP_AMOUNT = 3
SCALE_BBOX = 0.5
tmp_dir = os.path.join(os.getcwd(),"tmp")
tmp_crop = os.path.join(tmp_dir, "crop.png")
tmp_mask = os.path.join(tmp_dir, "mask.png")

# -----------------------  GERAL  --------------------------- #
CAMERA_INDEX = 0
MAX_IPS = 1 # Maximum number of iterations per second

# ------------------ PINOS RASPBERRY Pi --------------------- #
# MOSFETs Toggle
ToggleLED, ToggleServo = 18, 16
# Servos
Servo_Dispenser_Cima = -1
Servo_Dispenser_Baixo = -1
Servo_Plataforma = -1
# Motor de Passo
Direcao_SM = -1
Passo_SM = -1
# Lista de Pinos usados
Pinos = [
         ToggleLED, 
         ToggleServo,
         Servo_Dispenser_Cima,
         Servo_Dispenser_Baixo,
         Servo_Plataforma,
         Direcao_SM,
         Passo_SM
        ]

# ------------------ SETUP RASPBERRY PI --------------------- #
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Pinos, GPIO.OUT)

minDeltaT = 1e-5 # sec
stepsPerRevolution = 200

# ----------------------------------------------------------- #



# ----------------------------------------------------------- #