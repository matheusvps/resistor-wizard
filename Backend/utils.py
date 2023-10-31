# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
import numpy as np
import cv2 as cv
import os
from time import time, sleep

CROP_AMOUNT = 3
SCALE_BBOX = 0.5
tmp_dir = os.path.join(os.getcwd(),"tmp")
tmp_crop = os.path.join(tmp_dir, "crop.png")
tmp_mask = os.path.join(tmp_dir, "mask.png")
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Crops a numpy array image using a bounding box
def cropImage(image, box):
    return image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]


# Calculates the centroid of a rectangle
def get_centroid(rect):
    cX = (rect[2] + rect[0])/2
    cY = (rect[3] + rect[1])/2
    return (cX, cY)


# Checks if two colors are equal
def eqq(a,b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
                return False
    return True

# Calculates the equivalent vector sum of two vectors/colors
def vec_sum(v1, v2):
    if len(v1) != len(v2):
        raise Exception("Lengths of vectors passed are not the same")
    out = [0]*len(v1)
    for i in range(len(v1)):
        out[i] = v1[i] + v2[i]
    return out

# Class mask for grouping objects
class Mask:
    def __init__(self, img, bbox=[], contour=[]):
        self.image = img
        self.mask = np.zeros_like(img, dtype=np.uint8)  # creates mask of same size as original image
        self.avgColor = (None, None, None)
        self.bbox = bbox
        self.contour = contour
        self.index = -1  # This color's position relative to others
        self.color = ""  # A string identifier of the color the mask represents
    # Calculates average color on the color band associated with the mask
    def sample_avg_color(self):
        center = [int(j) for j in get_centroid([float(i) for i in self.bbox[:4]])]  # Center of Bounding box
        xLength = self.bbox[2] - self.bbox[0]  # Length of edges on X and Y
        yLength = self.bbox[3] - self.bbox[1]
        sX = int(center[0] - ((SCALE_BBOX*xLength)/2))  # Top left corner of box to consider for averaging
        sY = int(center[1] - ((SCALE_BBOX*yLength)/2))
        eX = int(sX + (SCALE_BBOX*xLength))
        eY = int(sY + (SCALE_BBOX*yLength))
        summ = np.array([0,0,0])
        nump = 0
        for i in range(sX, eX+1):
            for j in range(sY, eY+1):
                if cv.pointPolygonTest(self.contour, (i, j), measureDist=False) == 1:
                    summ += self.image[j][i]
                    nump += 1
        self.avgColor = summ/nump
        
    # Checks if a point is inside the mask's bounding box
    def contains(self, point):
        if list(point) < self.bbox[0:2].tolist() or list(point) > self.bbox[2:4].tolist():
            return False
        else:
            return True


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
    for i in range(len(inference[0].masks.xy)):
        polygon = inference[0].masks.xy[i].astype(int)
        masks[i].contour = polygon
        masks[i].bbox = inference[0].boxes.cpu().data[i]
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

    ordered = list(sorted_masks)
    for m in ordered:
        m.index = ordered.index(m)
    return ordered


# Runs and records the execution time of a function
def timer(func, *args, printout=False):
    """
        Times the execution of a function\n
        Arguments:\n
            func: function to be timed\n
            *args: occasional arguments to be passed to the function called\n
            printout: wheter to print to console or not\n
        Output:\n
            res: the output from the function ran\n
            dt = time elapsed since beginning and end of the function\n
    """
    start = time()
    res = func(*args)
    end = time()
    dt = end - start
    if printout:
        print(f"Function \033[94m {func.__name__} \033[0m took {dt:.{2}f}s to run.")
    return res, dt




