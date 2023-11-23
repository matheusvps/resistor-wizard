# ----------------------  IMPORTS  -------------------------- #
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2 as cv
from time import time, sleep
import os, sys
from multiprocessing import Process, Value, Array
import json
import ctypes
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin

import RPi.GPIO as GPIO

# ----------------------------------------------------------- #


CROP_AMOUNT = 3
SCALE_BBOX = 0.5
tmp_dir = os.path.join(os.getcwd(),"tmp")
tmp_photo = os.path.join(tmp_dir, "photo.png")
tmp_crop = os.path.join(tmp_dir, "crop.png")
tmp_mask = os.path.join(tmp_dir, "mask.png")

# -----------------------  GERAL  --------------------------- #
CAMERA_INDEX = -1
CAMERA_FOCUS = 0
CAMERA_EXPOSURE = 1023
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
Hall_effect = -1
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
GPIO.setmode(GPIO.BOARD)
for pino in Pinos:
    GPIO.setup(pino, GPIO.OUT)

minDeltaT = 2e-6 # 2u sec
stepsPerRevolution = 200

# ------------------ RECEIVER VARIABLES ----------------------------------- #
PORT = 5000
IP = "0.0.0.0"


# ----------------------------------------------------------- #