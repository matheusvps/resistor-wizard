from utils import *
from PIL import ImageDraw

file = "../Fotos_to_train/0001.png"

color_bands = YOLO("LATEST/color_band_segment_grayscale.pt")
colorbands_infr = color_bands(file, conf=0.6, iou=0.3)

masks, _ = timer(get_segmentation_masks, file, colorbands_infr, printout=True)

ordered, _ = timer(order_masks, masks, colorbands_infr, printout=True)

labeled = Image.open(file)
for i in range(len(ordered)):
    ImageDraw.Draw(labeled).text((ordered[i].bbox[0], ordered[i].bbox[1]), str(i), fill=(255,0,0))
labeled.save("labeled.png")

for i in range(len(ordered)):
    print(f"BBOX: {[int(j) for j in ordered[i].bbox[:4]]} \t Index: {ordered[i].index} \t HSV: {cvtBGR2HSV(ordered[i].avgColor, paint=True)}")

