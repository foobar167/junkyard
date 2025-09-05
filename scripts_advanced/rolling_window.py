# Rolling window for 2D arrays in NumPy
import numpy as np

def rolling_window(a, shape):  # rolling window for 2D array
    s = (a.shape[0] - shape[0] + 1,) + (a.shape[1] - shape[1] + 1,) + shape
    strides = a.strides + a.strides
    return np.lib.stride_tricks.as_strided(a, shape=s, strides=strides)

a = np.array([[0,  1,  2,  3,  4,  5],
              [6,  7,  8,  9, 10,  11],
              [12, 13, 14, 15, 7,   8],
              [18, 19, 20, 21, 13, 14],
              [24, 25, 26, 27, 19, 20],
              [30, 31, 32, 33, 34, 35]], dtype=np.int)
b = np.arange(36, dtype=np.float).reshape(6,6)
# Array present is occurred in array a two times on [1,1] and [2,4].
present = np.array([[7,8],[13,14],[19,20]], dtype=np.int)
absent  = np.array([[7,8],[42,14],[19,20]], dtype=np.int)

found = np.all(np.all(rolling_window(a, present.shape) == present, axis=2), axis=2)
print(np.transpose(found.nonzero()))
found = np.all(np.all(rolling_window(b, present.shape) == present, axis=2), axis=2)
print(np.transpose(found.nonzero()))
found = np.all(np.all(rolling_window(a, absent.shape) == absent, axis=2), axis=2)
print(np.transpose(found.nonzero()))

x = np.array([[1,2],[3,4],[5,6],[7,8],[9,10],[3,4],[5,6],[7,8],[11,12]])
y = np.array([[3,4],[5,6],[7,8]])
found = np.all(np.all(rolling_window(x, y.shape) == y, axis=2), axis=2)
print(found.nonzero()[0])
