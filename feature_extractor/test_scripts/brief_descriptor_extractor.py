# BRIEF (Binary Robust Independent Elementary Features) descriptor
import cv2
import numpy as np

# Read and convert the image to grayscale
imname = '../data/2023.06.23_book_cover.jpg'
image = cv2.imread(imname)
if image is None:
    print(f'Cannot read image "{imname}"')
    exit(-1)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Initiate FAST detector
star = cv2.xfeatures2d.StarDetector_create()

# Initiate BRIEF extractor
brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()

# Find the keypoints with STAR (CenSurE) feature detector
kp = star.detect(gray_image, None)

# Compute the descriptors with BRIEF
kp, des = brief.compute(gray_image, kp)

print(brief.descriptorSize())
print(des.shape)

kp_image = cv2.drawKeypoints(image, kp, None, color=(0, 255, 0))

cv2.imshow('STAR (CenSurE) detector and BRIEF descriptor', kp_image)
cv2.waitKey()
