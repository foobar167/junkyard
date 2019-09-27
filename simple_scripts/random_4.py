"""
  How to generate a random 4 digit number
  not starting with 0 and having unique digits in python?

  Solution: randomly shuffle all numbers. If 0 is on the 0th position,
              randomly swap it with any of nine positions in the list.

    Proof
    Lets count probability for 0 to be in position 7. It is equal to probability 1/10
  after shuffle, plus probability to be randomly swapped in the 7th position if
  0 come to be on the 0th position: (1/10 * 1/9). In total: (1/10 + 1/10 * 1/9).
    Lets count probability for 3 to be in position 7. It is equal to probability 1/10
  after shuffle, minus probability to be randomly swapped in the 0th position (1/9)
  if 0 come to be on the 0th position (1/10) and if 3 come to be on the 7th position
  when 0 is on the 0th position (1/9). In total: (1/10 - 1/9 * 1/10 * 1/9).
    Total probability of all numbers [0-9] in position 7 is:
  9 * (1/10 - 1/9 * 1/10 * 1/9) + (1/10 + 1/10 * 1/9) = 1
    Continue to prove in the same way that total probability is equal to
  1 for all other positions.
    End of proof.
"""
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

