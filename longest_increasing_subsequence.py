l = [3,4,5,9,8,1,2,7,7,7,7,7,7,7,6,0,1]
empty = []
one = [1]
two = [2,1]
three = [1,0,2,3]
tricky = [1,2,3,0,-2,-1]
ring = [3,4,5,0,1,2]
internal = [9,1,2,3,4,5,0]

# consider your list as a ring, continuous and infinite
def longest_increasing_subsequence(l):
    length = len(l)
    if length == 0: return 0  # list is empty
    i, tmp, longest = [0, 1, 1]
    # 1 < tmp means that ring is finished, but the sequence continue to increase
    while i < length or 1 < tmp:
        # compare elements on the ring
        if l[i%length] < l[(i+1)%length]:
            tmp += 1
        else:
            if longest < tmp: longest = tmp
            tmp = 1
        i += 1
    return longest

print("0 == " + str(longest_increasing_subsequence(empty)))
print("1 == " + str(longest_increasing_subsequence(one)))
print("2 == " + str(longest_increasing_subsequence(two)))
print("3 == " + str(longest_increasing_subsequence(three)))
print("5 == " + str(longest_increasing_subsequence(tricky)))
print("5 == " + str(longest_increasing_subsequence(internal)))
print("6 == " + str(longest_increasing_subsequence(ring)))
print("6 == " + str(longest_increasing_subsequence(l)))

