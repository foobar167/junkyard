""" Apply different filters here """
import cv2  # import OpenCV 3 module
import numpy as np

camera = cv2.VideoCapture(0)  # get default camera
mode = 2  # default mode, apply Canny edge detection
while True:
    ok, frame = camera.read()  # read frame
    if not ok: continue  # skip underlying part, if frame didn't read correctly

    if mode == 2:
        frame = cv2.Canny(frame, 100, 200)  # Canny edge detection
    if mode == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale
        frame = cv2.Canny(frame, 100, 200)  # Canny edge detection
    if mode == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale
        frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                      cv2.THRESH_BINARY, 11, 2)  # adaptive Gaussian thresholding
    if mode == 5:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray, 2, 23, 0.04)  # 3rd parameter is odd and must be [3,31]
        frame[dst > 0.01 * dst.max()] = [0, 0, 255]
    if mode == 6:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        keypoints, descriptor = sift.detectAndCompute(gray, None)
        frame = cv2.drawKeypoints(image=frame, outImage=frame, keypoints=keypoints,
                                  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))

    cv2.imshow('My camera', frame)  # show frame
    key = cv2.waitKey(1) & 0xff  # read keystroke
    if key == 255: continue  # skip underlying part, if key hasn't been pressed
    if key == 27: break  # <Escape> key pressed, exit from cycle
    if key == ord('1'): mode = 1  # show unchanged frame
    if key == ord('2'): mode = 2  # apply Canny edge detection
    if key == ord('3'): mode = 3  # apply Canny to gray frame
    if key == ord('4'): mode = 4  # adaptive Gaussian thresholding
    if key == ord('5'): mode = 5  # detect corners in an image
    if key == ord('6'): mode = 6  # Scale-Invariant Feature Transform (SIFT)

camera.release()  # release web camera
cv2.destroyAllWindows()
