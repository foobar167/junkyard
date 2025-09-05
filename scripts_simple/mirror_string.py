def mirror(s):
    return s + s[::-1]


def is_mirror(s):
    length = len(s)
    if length % 2:  # mirrored string is always odd
        return False
    else:  # compare two halves of the string
        half = length >> 1  # divide by 2
        return s[:half] == s[half:][::-1]

mirror('abcd')
is_mirror('abcd')
is_mirror('xyzzyx')
