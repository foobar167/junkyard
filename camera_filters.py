""" Apply different filters here """

import cv2  # import OpenCV 3 module

camera = cv2.VideoCapture(0)  # get default camera
mode = 2  # default mode, apply Canny edge detection
while True:
    ok, frame = camera.read()  # read frame
    if ok:  # frame is read correctly
        if mode == 2:
            frame = cv2.Canny(frame, 100, 200)  # Canny edge detection
        cv2.imshow('My camera', frame)  # show frame
    key = cv2.waitKey(1) & 0xff  # read keystroke
    if key == 27: break  # <Escape> key pressed, exit from cycle
    if key == ord('1'): mode = 1  # show unchanged frame
    if key == ord('2'): mode = 2  # apply Canny edge detection

camera.release()  # release web camera
cv2.destroyAllWindows()
