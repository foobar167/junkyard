# Find the highest number not in the list
import numpy as np

l = [1, 3, 5, 9, 11]
a = np.array(l)
ans = 1
for i in range(a.max(initial=0) - 1, max(0, a.min(initial=0)), -1):
    if i not in a:
        ans = i
        print(i)
        break

A = [1, 3, 5, 9, 11]
Ans = 1
for j in range(max(A)-1, max(0, min(A)), -1):
    if j not in A:
        Ans = j
        print(Ans)
        break
