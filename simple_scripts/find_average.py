def average(lst):
    """ Count average from the list of numbers """
    return sum(lst) / len(lst)


positive = []  # list of positive numbers
negative = []  # list of negative numbers
num = None

print("(enter '0' to stop)")
while True:
    try:  # try to enter float values
        num = float(input('enter value: '))
    except ValueError:  # non-number was entered
        print('please, enter only numbers')
        continue  # start from beginning of while loop

    if num > 0:  # if positive, append number to positive list
        positive.append(num)
    elif num < 0:  # if negative, append number to negative list
        negative.append(num)
    else:  # if zero, exit from the while loop
        break

# Use f-strings to print for Python 3.7 and higher
if len(positive):
    print(f'positive average: {average(positive)}')
if len(negative):
    print(f'negative average: {average(negative)}')
if len(positive) == 0 and len(negative) == 0:
    print('no values were entered')
