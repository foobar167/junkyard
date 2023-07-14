# Haris corner detection
# URL: https://www.geeksforgeeks.org/feature-detection-and-matching-with-opencv-python/
import cv2

# Read and convert the image to grayscale
imname = '../data/2023.06.23_book_cover.jpg'
image = cv2.imread(imname)
if image is None:
    print(f'Cannot read image "{imname}"')
    exit(-1)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Applying the function
dst = cv2.cornerHarris(gray_image, blockSize=2, ksize=3, k=0.04)

# Dilate to mark the corners
dst = cv2.dilate(dst, None)
image[dst > 0.01 * dst.max()] = [0, 255, 0]

cv2.imshow('Haris corner detection', image)
cv2.waitKey()
