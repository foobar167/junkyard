""" How to generate a random 4 digit number not starting with 0 and having unique digits in python? """

import random

# 1.
l = [0,1,2,3,4,5,6,7,8,9]
random.shuffle(l)
if l[0] == 0:
    pos = random.choice(range(1, len(l)))
    l[0], l[pos] = l[pos], l[0]
print(''.join(map(str, l[0:4])))

# 2.
# We create a set of digits: {0, 1, .... 9}
digits = set(range(10))
# We generate a random integer, 1 <= first <= 9
first = random.randint(1, 9)
# We remove it from our set, then take a sample of
# 3 distinct elements from the remaining values
last_3 = random.sample(digits - {first}, 3)
print(str(first) + ''.join(map(str, last_3)))

# 3.
numbers = [0]
while numbers[0] == 0:
    numbers = random.sample(range(10), 4)
print(''.join(map(str, numbers)))

