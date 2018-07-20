import numpy as np
from PIL import Image, ImageDraw

width = 10
height = 10
polygon = [(1,2), (9,1), (5,8)]

img = Image.new('L', (width, height), 0)  # using gray 'L' array for debug purposes
#img = Image.new('1', (width, height), 0)  # better to use bitwise '1' array
ImageDraw.Draw(img).polygon(polygon, fill=1)
mask = np.array(img)
print(mask, '\n')
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)
print(mask, '\n')
ImageDraw.Draw(img).polygon(polygon, outline=0, fill=1)
mask = np.array(img)
print(mask, '\n')
