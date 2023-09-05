import time
import numpy as np

n = 2000
A = np.random.randn(n, n).astype('float64')
B = np.random.randn(n, n).astype('float64')
start_time = time.time()
nrm = np.linalg.norm(A@B)
print(f"Took {time.time() - start_time} seconds ")
print(f"Norm = {nrm}\n")
print(np.__config__.show())
