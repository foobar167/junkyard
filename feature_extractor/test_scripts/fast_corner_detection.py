# FAST algorithm for corner detection
import cv2

# Read and convert the image to grayscale
imname = '../data/2023.06.23_book_cover.jpg'
image = cv2.imread(imname)
if image is None:
    print(f'Cannot read image "{imname}"')
    exit(-1)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Applying the function
fast = cv2.FastFeatureDetector_create()
fast.setNonmaxSuppression(False)

# Drawing the keypoints
kp = fast.detect(gray_image, None)
kp_image = cv2.drawKeypoints(image, kp, None, color=(0, 255, 0))

print(dir(kp[0]), '\n point example: ', kp[1].pt)

cv2.imshow('FAST algorithm for corner detection', kp_image)
cv2.waitKey()
