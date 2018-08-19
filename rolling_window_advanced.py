# Rolling window for 2D arrays in NumPy
import numpy as np
from PIL import Image, ImageDraw

# Rolling window for 2D array
def roll(a,    # image array
         b,    # rolling window array
         dx,   # horizontal step - number of columns
         dy):  # vertical step - number of rows
    shape = (int((a.shape[0] - b.shape[0]) / dy) + 1,) + \
            (int((a.shape[1] - b.shape[1]) / dx) + 1,) + b.shape
    strides = (a.strides[0] * dy, a.strides[1] * dx,) + a.strides
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

a = np.array([[0,  1,  2,  3,  4,  5],
              [7,  8,  7,  8, 10,  11],
              [13, 14, 13, 14, 7,   8],
              [19, 20, 19, 20, 13, 14],
              [24, 25, 26, 27, 19, 20],
              [30, 31, 32, 33, 34, 35]], dtype=np.int)
c = np.arange(36, dtype=np.float).reshape(6,6)
# Array present is occurred in array a two times on [1,1] and [2,4].
present = np.array([[7,8],[13,14],[19,20]], dtype=np.int)
absent  = np.array([[7,8],[42,14],[19,20]], dtype=np.int)

dx, dy = 1, 1
found = np.all(np.all(roll(a, present, dx, dy) == present, axis=2), axis=2)
print(np.transpose(found.nonzero()) * [dy, dx])
dx, dy = 2, 1
found = np.all(np.all(roll(a, present, dx, dy) == present, axis=2), axis=2)
print(np.transpose(found.nonzero()) * [dy, dx])
dx, dy = 1, 1
found = np.all(np.all(roll(c, present, dx, dy) == present, axis=2), axis=2)
print(np.transpose(found.nonzero()) * [dy, dx])
dx, dy = 1, 1
found = np.all(np.all(roll(a, absent, dx, dy) == absent, axis=2), axis=2)
print(np.transpose(found.nonzero()) * [dy, dx])

x = np.array([[1,2],[3,4],[5,6],[7,8],[9,10],[3,4],[5,6],[7,8],[11,12]])
y = np.array([[3,4],[5,6],[7,8]])
dx, dy = 1, 1
found = np.all(np.all(roll(x, y, dx, dy) == y, axis=2), axis=2)
print(found.nonzero()[0] * dy)

#print(roll(a, present, 2, 1))  # debug

width = 10
height = 10
polygon = [(1,2), (9,1), (5,8)]

img = Image.new('L', (width, height), 0)  # using gray 'L' array for debug purposes
ImageDraw.Draw(img).polygon(polygon, fill=1)
mask = np.array(img)
print(mask, '\n')
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)
print(mask, '\n')
ImageDraw.Draw(img).polygon(polygon, outline=0, fill=1)
mask = np.array(img)
print(mask, '\n')

img = Image.new('1', (width, height), False)  # better to use bitwise '1' array
ImageDraw.Draw(img).polygon(polygon, outline=True, fill=True)
mask = np.array(img, dtype=np.bool)

rolling_window = np.full((2, 2), True, dtype=np.bool)
dx, dy = 1, 1
found = np.all(np.all(roll(mask, rolling_window, dx, dy) == rolling_window, axis=2), axis=2)
print(np.transpose(found.nonzero()) * [dy, dx])
