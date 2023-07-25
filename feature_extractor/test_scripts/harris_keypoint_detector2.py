# Project: Detect the Corners of Objects Using Harris Corner Detector
# Author: Addison Sears-Collins
# Date created: October 7, 2020
# Reference: https://stackoverflow.com/questions/7263621/how-to-find-corners-on-a-image-using-opencv/50556944

import cv2  # OpenCV library
import numpy as np  # NumPy scientific computing library
import math  # Mathematical functions

# The file name of your image goes here
fileName = '../data/tshirt.jpg'

# Read the image file
img = cv2.imread(fileName)

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

######## The code in this block is optional #########
## Turn the image into a black and white image and remove noise
## using opening and closing

# gray = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)[1]

# kernel = np.ones((5,5),np.uint8)

# gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
# gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

## To create a black and white image, it is also possible to use OpenCV's
## background subtraction methods to locate the object in a real-time video stream
## and remove shadows.
## See the following links for examples
## (e.g. Absolute Difference method, BackgroundSubtractorMOG2, etc.):
## https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/
## https://automaticaddison.com/motion-detection-using-opencv-on-raspberry-pi-4/

############### End optional block ##################

# Apply a bilateral filter.
# This filter smooths the image, reduces noise, while preserving the edges
bi = cv2.bilateralFilter(gray, 5, 75, 75)

# Apply Harris Corner detection.
# The four parameters are:
#   The input image
#   The size of the neighborhood considered for corner detection
#   Aperture parameter of the Sobel derivative used.
#   Harris detector free parameter
#   --You can tweak this parameter to get better results
#   --0.02 for tshirt, 0.04 for washcloth, 0.02 for jeans, 0.05 for contour_thresh_jeans
#   Source: https://docs.opencv.org/3.4/dc/d0d/tutorial_py_features_harris.html
dst = cv2.cornerHarris(bi, 2, 3, 0.02)

# Dilate the result to mark the corners
dst = cv2.dilate(dst, None)

# Create a mask to identify corners
mask = np.zeros_like(gray)

# All pixels above a certain threshold are converted to white
mask[dst > 0.01 * dst.max()] = 255

# Convert corners from white to red.
# img[dst > 0.01 * dst.max()] = [0, 0, 255]

# Create an array that lists all the pixels that are corners
coordinates = np.argwhere(mask)

# Convert array of arrays to lists of lists
coordinates_list = [l.tolist() for l in list(coordinates)]

# Convert list to tuples
coordinates_tuples = [tuple(l) for l in coordinates_list]

# Create a distance threshold
thresh = 50

# Compute the distance from each corner to every other corner.
def distance(pt1, pt2):
    (x1, y1), (x2, y2) = pt1, pt2
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

# Keep corners that satisfy the distance threshold
coordinates_tuples_copy = coordinates_tuples
i = 1
for pt1 in coordinates_tuples:
    for pt2 in coordinates_tuples[i::1]:
        if (distance(pt1, pt2) < thresh):
            coordinates_tuples_copy.remove(pt2)
    i += 1

# Place the corners on a copy of the original image
img2 = img.copy()
for pt in coordinates_tuples:
    print(tuple(reversed(pt)))  # Print corners to the screen
    cv2.circle(img2, tuple(reversed(pt)), 10, (0, 0, 255), -1)
cv2.imshow('Image with 4 corners', img2)
# cv2.imwrite('harris_corners_jeans.jpg', img2)

# Exit OpenCV
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
