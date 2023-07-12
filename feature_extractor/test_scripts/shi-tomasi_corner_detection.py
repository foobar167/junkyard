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
corners = cv2.goodFeaturesToTrack(gray_image, maxCorners=3, qualityLevel=0.02, minDistance=20)
corners = np.squeeze(corners).astype(int)  # squeeze dimensions and convert from float to int

# print(corners)
# print(corners[:, 1], corners[:, 0])
image[corners[:, 1], corners[:, 0]] = [0, 0, 255]  # set red dots, doesn't work
# image[[213, 213, 206], [41, 79, 484]]= [0, 0, 255]  # this works

for i in corners:
    cv2.circle(image, tuple(i), 5, (0, 255, 0), -1)

# Showing the image
cv2.imshow('Shi-Tomasi corner detection', image)
cv2.waitKey()
