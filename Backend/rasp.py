# All imports needed
from ultralytics import YOLO
import os
import cv2 as cv
import numpy as np
from PIL import Image
import csv

CROP_AMOUNT = 3
tmp_dir = os.path.join(os.getcwd(),"tmp")
tmp_crop = os.path.join(tmp_dir, "crop.png")
tmp_mask = os.path.join(tmp_dir, "mask.png")
if not os.path.isdir(tmp_dir):
    os.makedirs(tmp_dir)

cropResistor = YOLO("./LATEST/cropper.pt")
findColorBands = YOLO("./LATEST/segmenter.pt")

# Crops a numpy array image using a bounding box
def cropImage(image, box):
    return image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Checks if two colors are equal
def eqq(a,b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
                return False
    return True

# Class mask for grouping objects
class Mask:
    def __init__(self, img, bbox=[], contour=[]):
        self.image = img
        self.orig_shape = img.shape
        self.mask = np.zeros_like(img, dtype=np.uint8)  # creates mask of same size as original image
        self.size = -1  # Number of non-zero pixels
        self.avgColor = (None, None, None)
        self.bbox = bbox
        self.contour = contour
        self.index = -1  # This color's position relative to others
        self.color = ""  # A string identifier of the color the mask represents
        self.rotated = False
    # Bitwise AND on the original image using the mask
    def maskImage(self, crop=1):
        pixels = np.zeros_like(self.image, dtype=np.uint8)
        for x in range(len(self.image)):
            for y in range(len(self.image[0])):
                if eqq(self.mask[x][y], [255,255,255]):
                    if x-crop >= 0 and x+crop < len(self.image) and y-crop >= 0 and y+crop < len(self.image[0]):
                        if eqq(self.mask[x-crop][y], [255,255,255]) and eqq(self.mask[x+crop][y], [255,255,255]) and eqq(self.mask[x][y-crop], [255,255,255]) and eqq(self.mask[x][y+crop], [255,255,255]):
                            pixels[x][y] = self.image[x][y]
                        else:
                            self.size -= 1
        return pixels
    # Calculates average color on the color band associated with the mask
    def sample_avg_color(self):
        pixels = self.maskImage(crop=CROP_AMOUNT)
        self.avgColor = np.sum(pixels.reshape((-1,1,3)), axis=0) / self.size   
    # Checks if a point is inside the mask's bounding box
    def contains(self, point):
        if list(point) < self.bbox[0:2].tolist() or list(point) > self.bbox[2:4].tolist():
            return False
        else:
            return True

# Calculates the centroid of a rectangle
def get_centroid(vertex):
    cX = (vertex[2] + vertex[0])/2
    cY = (vertex[3] + vertex[1])/2
    return (cX, cY)

# Calculates the linear regression of the points in a 2D dataset: Y in function of X (Y= a*X + b)
def lin_reg(data):
    X = np.array([i[0] for i in data])
    Y = np.array([i[1] for i in data])
    a = ((len(data) * np.sum(X*Y)) - (np.sum(X) * np.sum(Y)))/(len(data) * np.sum(X*X) - (np.sum(X))**2)
    b = ((np.sum(Y) * np.sum(X*X)) - (np.sum(X) * np.sum(X*Y)))/(len(data) * np.sum(X*X) - (np.sum(X))**2)
    return a,b

# Converts BGR color to HSV (0-360, 0-255, 0-255)
def cvtBGR2HSV(bgr, paint=False):
    B,G,R = bgr
    Rp = R/255 
    Gp = G/255 
    Bp = B/255
    Cmax = max(Rp, Gp, Bp)
    Cmin = min(Rp, Gp, Bp)
    delta = Cmax - Cmin
    #
    if delta == 0:
        H = 0
    elif Cmax == Rp:
        H = 60 * (((Gp - Bp) / delta) % 6)
    elif Cmax == Gp:
        H = 60 * (((Bp - Rp) / delta) + 2)
    elif Cmax == Bp:
        H = 60 * (((Rp - Gp) / delta) + 4)
    #
    if Cmax == 0:
        S = 0
    else:
        S = delta/Cmax
    #
    V = Cmax

    if paint:
        S *= 100
        V *= 100
    else:
        S *= 255
        V *= 255
    return [int(i) for i in (H,S,V)]
    

# Retrieves the pixels contained in the contours given by the model prediction
def get_segmentation_masks(img, inference, data=255):
    image = cv.imread(img)
    masks = [Mask(image) for i in range(len(inference[0].masks.xy))]
    #
    for i in range(len(inference[0].masks.xy)):
        polygon = inference[0].masks.xy[i].astype(int)
        masks[i].bbox = inference[0].boxes.cpu().data[i]
        masks[i].contour = polygon.reshape((-1, 1, 2))  # Reshape to match the format expected by cv.drawContours
        masks[i].mask = cv.fillPoly(masks[i].mask, [masks[i].contour], (data, data, data)) # converts polygon points to pixels inside it
        masks[i].size = 0
        for j in masks[i].mask.reshape((-1,1,3)):
            if not eqq(j[0], [0,0,0]):
                masks[i].size += 1
        masks[i].sample_avg_color()
    return masks

# Finds the mask that contains a given point – considers a point can belong to a single mask
def retrieve_point_in_mask(masks, point):
    for mask in masks:
        if mask.contains(point):
            return mask

# Calculates the possible orders of the color bands – assumes the bands are approximately
#     linear, which is reasonable given that resistors follow this standard
def order_masks(masks, inference):
    boxes = inference[0].boxes.cpu().data
    vertex = [v[:4] for v in boxes]
    centroids = [get_centroid(v) for v in vertex]
    #
    # Calculates the line that approximately crosses the centroids – it's used to find the order in which the bands are disposed
    parameters = lin_reg(centroids)
    lv = np.array([1,parameters[0]]) # Line Vector
    lv_norm = np.sqrt(sum(lv**2))
    #
    vects = {}
    for center in centroids:
        u = np.array(center) - np.array([0,parameters[1]])  # Calculates the vector from the origin of the line to the centroid
        proj = lv * np.dot(u,lv) / (lv_norm**2)  # Projects the centroid onto the line
        vects[retrieve_point_in_mask(masks, center)] = np.sqrt(np.sum(proj**2))  # Calculates each centroid's distance to origin and associates it to its respective mask
    # Sorts masks by distance
    sorted_masks = dict(sorted(vects.items(), key=lambda item: item[1]))

    #if len(sorted_masks) != len(masks):
    #  ~ TERMINAR CODIGO DE ROTAÇÃO DAS IMAGENS CASO ESTEJA VERTICAL... ~
    return list(sorted_masks)


# Converts HSV values to paint's standard
def cvtHSV(hsv):
    return [int(i) for i in [hsv[0]*2, 0.3922*hsv[1], 0.3922*hsv[2]]]


file = "./Functionality Tests/0009.png"

# Runs crop detection model on file
cropped_inf = cropResistor(file, conf=0.6)

# Crops and saves original file to a temporary location
if len(cropped_inf[0].boxes.data):
    cropped = cropImage(cv.imread(file), cropped_inf[0].boxes.cpu().data[0])
else:
    cropped = cv.imread(file)
Image.fromarray(cv.cvtColor(cropped, cv.COLOR_BGR2RGB)).save(tmp_crop)

# Runs color bands segmentation model on cropped inference
if len(cropped_inf[0].boxes.data):
    colorbands_inf = findColorBands(tmp_crop, save=True, conf=0.6, iou=0.3)
else:
    colorbands_inf = findColorBands(file, save=True, conf=0.6, iou=0.3)


# Gets masks objects from the inference
masks = get_segmentation_masks(tmp_crop, colorbands_inf)

# Sorts the masks by distance (it doesn't have a way to 
#    know in which direction to start, so by default it 
#    uses the leftmost (0,0) point as a beginning.
ordered = order_masks(masks, colorbands_inf)