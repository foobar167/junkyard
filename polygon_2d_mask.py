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

width = 31
height = 31
polygon = [(2,1), (5,29), (29,4), (25,23)]
img = Image.new('L', (width, height), 0)  # using gray 'L' array for debug purposes
#img = Image.new('1', (width, height), 0)  # better to use bitwise '1' array
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)
print(mask, '\n')

width = 31
height = 31
polygon = [(8,29), (15,1), (22,29), (4,11), (26,11)]
img = Image.new('L', (width, height), 0)  # using gray 'L' array for debug purposes
#img = Image.new('1', (width, height), 0)  # better to use bitwise '1' array
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)
print(mask, '\n')

width = 31
height = 31
polygon = [(12,29), (15,1), (22,29), (4,6), (26,6), (1,15)]
img = Image.new('L', (width, height), 0)  # using gray 'L' array for debug purposes
#img = Image.new('1', (width, height), 0)  # better to use bitwise '1' array
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)
print(mask, '\n')

from skimage.draw import polygon
img = np.zeros((31, 31), dtype=np.uint8)
r = np.array([29, 1, 29, 11, 11])
c = np.array([8, 15, 22, 4, 26])
rr, cc = polygon(r, c)
img[rr, cc] = 1
print(img)
