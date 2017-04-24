""" How to generate a random 4 digit number not starting with 0 and having unique digits in python? """

import random
l = [0,1,2,3,4,5,6,7,8,9]
random.shuffle(l)
if l[0] == 0:
    print(''.join(map(str, l[1:5])))
else:
    print(''.join(map(str, l[0:4])))
