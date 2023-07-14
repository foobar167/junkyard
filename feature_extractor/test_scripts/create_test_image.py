import cv2
import numpy as np

w, h = 40, 20
# Make empty black image
image = np.zeros((h, w, 3), np.uint8)

# Fill left half with yellow (Blue, Green, Red)
image[:, 0:int(w/2)] = (0, 255, 255)

# Fill right half with sky blue (B, G, R)
image[:, int(w/2):w] = (235, 206, 135)

# Create a named colour
red = [0, 0, 255]

# Change one pixel
image[10, 5] = red

# cv2.imwrite('result.png', image)  # save
cv2.imshow('Set one dot', image)
cv2.waitKey()
