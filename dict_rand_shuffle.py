import random

d1 = {0:'zero', 1:'one', 2:'two', 3:'three', 4:'four',
     5:'five', 6:'six', 7:'seven', 8:'eight', 9:'nine'}

keys = list(d1)
random.shuffle(keys)

d2 = {}
for key in keys: d2[key] = d1[key]

print(d1)
print(d2)
