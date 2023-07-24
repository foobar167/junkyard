# Shi-Tomasi corner detection
# Find only the N strongest corners of the image.
import cv2
import numpy as np

# Read and convert the image to grayscale
imname = '../data/2023.06.23_book_cover.jpg'
image = cv2.imread(imname)
if image is None:
    print(f'Cannot read image "{imname}"')
    exit(-1)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Applying the function
corners = cv2.goodFeaturesToTrack(gray_image, maxCorners=50, qualityLevel=0.02, minDistance=20)
corners = np.squeeze(corners).astype(int)  # squeeze dimensions and convert from float to int

for i in corners:
    cv2.circle(image, tuple(i), 5, (0, 255, 0), -1)  # set green cycle

image[corners[:, 1], corners[:, 0]] = (0, 0, 255)  # set red dots

# Showing the image
# cv2.imwrite('test.png', image)  # JPG codec doesn't write red dots correctly
cv2.imshow('Shi-Tomasi corner detection', image)
cv2.waitKey()
