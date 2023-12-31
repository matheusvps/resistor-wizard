# ----------------------  IMPORTS  -------------------------- #

from PIL import Image
import numpy as np
import cv2 as cv
from time import time, sleep
import os, sys
import concurrent.futures
from multiprocessing import Process, Value, Array
import json
import ctypes
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from multiprocessing.sharedctypes import SynchronizedBase
from typing import Any
import signal
from gpio_conf import *

# Disables YOLO prediction output
os.environ["YOLO_VERBOSE"] = "False"
from ultralytics import YOLO

GPIO = gpio()

SYSTEM = platform.system()
if SYSTEM != 'Windows':
    GPIO.enabled = True


# ----------------------------------------------------------- #

CROP_AMOUNT = 0
CENTER_BOX = 1/2

WORKINGDIR = os.path.dirname( os.path.abspath( __file__ ) )
tmp_dir = os.path.join(WORKINGDIR,"tmp")
if not os.path.isdir(tmp_dir):
    os.mkdir(tmp_dir)
tmp_photo = os.path.join(tmp_dir, "photo.png")
tmp_crop = os.path.join(tmp_dir, "crop.png")
tmp_mask = os.path.join(tmp_dir, "mask.png")

yolo_cropper = os.path.join(WORKINGDIR, "LATEST/cropper_retrained.pt")
yolo_segment = os.path.join(WORKINGDIR, "LATEST/color_band_segment_grayscale_v13.pt")

RESISTANCE_COLOR_VALUES = {
    'BLACK':0,
    'BROWN':1,
    'RED':2,
    'ORANGE':3,
    'YELLOW':4,
    'GREEN':5,
    'BLUE':6,
    'VIOLET':7,
    'GREY':8,
    'WHITE':9,
    'GOLD':5,     # TOLERANCE
    'SILVER':10,  # TOLERANCE
}

# -----------------------  GERAL  --------------------------- #
CAMERA_INDEX = -1
CAMERA_FOCUS = 400
CAMERA_EXPOSURE = 450
MAX_IPS = 10 # Maximum number of iterations per second

# ------------------ PINOS RASPBERRY Pi --------------------- #
# MOSFETs Toggle
ToggleLED, ToggleServo = 18, 16
# Servos
Servo_Dispenser_Cima = 11
Servo_Dispenser_Baixo = 13
Servo_Plataforma = 15
# Motor de Passo
Passo_SM = 3
Direcao_SM = 5
Sleep_SM = 12
# Sensor de efeito hall
Hall_effect = 7
# Lista de Pinos usados
Pinos = [
         ToggleLED, 
         ToggleServo,
         Servo_Dispenser_Cima,
         Servo_Dispenser_Baixo,
         Servo_Plataforma,
         Direcao_SM,
         Passo_SM,
         Sleep_SM
        ]

# ------------------ SETUP RASPBERRY PI --------------------- #
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
for pino in Pinos:
    GPIO.setup(pino, GPIO.OUT)
GPIO.setup(Hall_effect, GPIO.IN)

minDeltaT = 2e-6 # 2u sec
stepsPerRevolution = 200

# ------------------ RECEIVER VARIABLES ----------------------------------- #
PORT = 5000
IP = "0.0.0.0"


# ----------------------------------------------------------- #