# MSER (Maximally Stable Extremal Region extractor) detector of regions
import cv2
import numpy as np

mser = cv2.MSER.create()  # create MSER object
img = cv2.imread('../data/book_cover.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to gray scale
vis = img.copy()
regions, _ = mser.detectRegions(gray)  # detect regions in gray scale image
hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
cv2.polylines(vis, hulls, 1, (0, 255, 0))
cv2.imshow('img', vis)
cv2.waitKey(0)

mask = np.zeros((img.shape[0], img.shape[1], 1), dtype=np.uint8)
for contour in hulls:
    cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)

# This is used to find only text regions, remaining are ignored
text_only = cv2.bitwise_and(img, img, mask=mask)

cv2.imshow("text only", text_only)
cv2.waitKey(0)
