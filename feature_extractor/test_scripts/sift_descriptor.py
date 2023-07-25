# SIFT (Scale-Invariant Feature Transform)
import cv2

img = cv2.imread('../data/home.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
sift = cv2.SIFT.create()
kp = sift.detect(gray, None)
# img = cv2.drawKeypoints(gray, kp, img)
img = cv2.drawKeypoints(gray, kp, img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow('SIFT (Scale-Invariant Feature Transform) keypoints', img)
cv2.waitKey()
