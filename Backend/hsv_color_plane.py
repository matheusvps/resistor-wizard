import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import hsv_to_rgb

# Create figure and axes
fig, ax = plt.subplots()

S, H = np.mgrid[0:1:100j, 0:1:300j]
V = np.ones_like(S)
HSV = np.dstack((H,S,V))
RGB = hsv_to_rgb(HSV)
XYWH = [
    [0,0,300,35, 'GREY'],    # GREY
    [0,0,360,15, 'WHITE'],    # WHITE
    [0,50,8,50, 'RED'],     # RED LOW
    [310,50,50,50, 'RED'],  # RED HIGH
    [8,30,32,70, 'ORANGE'],    # ORANGE 1
    [0,0,15,50, 'ORANGE'],     # ORANGE 2
    [65,50,20,50, 'YELLOW'],   # YELLOW 1
    [40,65,25,35, 'YELLOW'],   # YELLOW 2
    [85,30,95,70, 'GREEN'],   # GREEN
    [165,75,80,25, 'BLUE'],  # BLUE
    [225,20,85,80, 'VIOLET'],  # VIOLET
]
for x,y,w,h,color in XYWH:
    rect = Rectangle([x,y], w, h, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2, color, fontsize=8, horizontalalignment='center', verticalalignment='center',)
ax.imshow(RGB, origin="lower", extent=[0, 360, 0, 100], aspect=3)

ax.set_xlabel("H")
ax.set_ylabel("S", rotation=0, labelpad=15)
ax.set_title("$V_{HSV}=1$")
plt.show()