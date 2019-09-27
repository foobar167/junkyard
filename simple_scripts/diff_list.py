# Return all numbers which differ from previous member on 2
# (including the 1st element).
import numpy as np

my_list = [1, 3, 5, 7, 14, 16, 18, 22, 28, 30, 32, 41, 43]
a = np.array(my_list)
mask = np.hstack(([True], a[1:] - a[:-1] != 2))
output = a[mask]
print(output)
