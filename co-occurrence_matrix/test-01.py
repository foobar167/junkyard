# -*- coding: utf-8 -*-
import numpy as np

dx = 1
dy = 0
a = np.array([[1,2,3,0,1,2],
              [6,5,4,2,1,2],
              [7,9,8,3,1,3],
              [5,4,1,2,3,1]], dtype=int)

comatrix1 = np.zeros((10,10), dtype=int)
h, w = a.shape
h -= dy
w -= dx
for i in range(h):
    for j in range(w):
        comatrix1[min(a[i, j], a[i+dy, j+dx]),
                  max(a[i, j], a[i+dy, j+dx])] += 1

mask =                           a[:h, :w] < a[dy:, dx:]
rows = np.where(mask,            a[:h, :w],  a[dy:, dx:])
cols = np.where(np.invert(mask), a[:h, :w],  a[dy:, dx:])
#print(mask)
#print(rows)
#print(cols)

comatrix2 = np.zeros((10,10), dtype=int)
np.add.at(comatrix2, [rows, cols], 1)

#print(comatrix1)
print(comatrix2)
print((comatrix1 == comatrix2).all())
