import cv2

img = cv2.imread('../data/jeans.jpg', cv2.IMREAD_GRAYSCALE)

# Initiate FAST object with default values
fast = cv2.FastFeatureDetector.create()

# Find and draw the keypoints
kp = fast.detect(img, None)
img2 = cv2.drawKeypoints(img, kp, None, color=(255, 0, 0))

# Print all default params
print(f"Threshold: {fast.getThreshold()}")
print(f"nonmaxSuppression:{fast.getNonmaxSuppression()}")
print(f"neighborhood: {fast.getType()}")
print(f"Total Keypoints with nonmaxSuppression: {len(kp)}")

cv2.imshow('nonmaxSuppression - True', img2)

# Disable nonmaxSuppression
fast.setNonmaxSuppression(0)
kp = fast.detect(img, None)

print(f"Total Keypoints without nonmaxSuppression: {len(kp)}")
img3 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
cv2.imshow('nonmaxSuppression - False', img3)

cv2.waitKey()
