# You can create structured arrays with combined data type.
# But numpy array unlike list cannot contain different data types
# All elements of numpy array have to be the same data type.
import numpy as np

dt = np.dtype([("iq",     np.uint8),
               ("status", np.unicode, 32),
               ("age",    np.uint8),
               ("mood",   np.unicode, 32),
               ("flag",   np.bool)])

a = np.loadtxt("file.csv", dtype=dt, delimiter=",")

print(a)
print(a[1:]["status"])
print(a[["age", "mood"]])
