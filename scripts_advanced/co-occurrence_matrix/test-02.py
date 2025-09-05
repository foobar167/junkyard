# -*- coding: utf-8 -*-
import timeit
import numpy as np
from PIL import Image

def get_rgb1():
    r = array[:, :, 0].astype(np.uint16) >> 5  # Red. Leave only 3 bit or 8 bins
    g = array[:, :, 1].astype(np.uint16) >> 5  # Green
    b = array[:, :, 2].astype(np.uint16) >> 5  # Blue
    return (r << 6) + (g << 3) + b  # rgb color consists of 9 bit or 512 tints

def get_rgb2():
    rgb = array.astype(np.uint16) >> 5  # leave only 3 bit or 8 bins
    r, g, b = np.dsplit(rgb, 3)  # split array on red, green and blue colors
    rgb = (r << 6) + (g << 3) + b  # rgb color consists of 9 bit or 512 tints
    return rgb.reshape(rgb.shape[:2])

def get_comatrix1():
    mask =                           rgb[:h, :w] < rgb[dy:, dx:]
    rows = np.where(mask,            rgb[:h, :w],  rgb[dy:, dx:])
    cols = np.where(np.invert(mask), rgb[:h, :w],  rgb[dy:, dx:])
    comatrix1 = np.zeros((512, 512), dtype=np.uint32)  # create 512x512 matrix
    np.add.at(comatrix1, [rows, cols], 1)
    return comatrix1

def get_comatrix2():
    comatrix2 = np.zeros((512, 512), dtype=np.uint32)  # verifying co-matrix
    for i in range(h):
        for j in range(w):
            comatrix2[min(rgb[i, j], rgb[i + dy, j + dx]),
                      max(rgb[i, j], rgb[i + dy, j + dx])] += 1
    return comatrix2

dx = 1
dy = 1
img = Image.open(u'../../data/doge.jpg')  # open image with PIL
array = np.array(img)  # convert PIL image to Numpy array

rgb  = get_rgb1()
rgb2 = get_rgb2()

print((rgb == rgb2).all())
n = 1000
print(timeit.timeit(stmt=u'get_rgb1()', number=n,
                    setup=u'from __main__ import get_rgb1') / n)
print(timeit.timeit(stmt=u'get_rgb2()', number=n,
                    setup=u'from __main__ import get_rgb2') / n)

h, w = rgb.shape
h -= dy
w -= dx

comatrix  = get_comatrix1()
comatrix2 = get_comatrix2()

print((comatrix == comatrix2).all())
n = 20
print(timeit.timeit(stmt=u'get_comatrix1()', number=n,
                    setup=u'from __main__ import get_comatrix1') / n)
print(timeit.timeit(stmt=u'get_comatrix2()', number=n,
                    setup=u'from __main__ import get_comatrix2') / n)
#print(comatrix1)
#print(comatrix2)

rows, cols = np.nonzero(comatrix)
descriptor = rows, cols, comatrix[rows, cols]
#print(descriptor)

# Restore co-occurrence matrix from descriptor
comatrix3 = np.empty((512, 512), dtype=np.uint32)
comatrix3[descriptor[0], descriptor[1]] = descriptor[2]
print((comatrix3 == comatrix).all())
