# This script displays a webcam feed (assuming that a webcam is plugged in).

import cv2  # import OpenCV 3 module

camera = cv2.VideoCapture(0)  # get default camera
while True:
    ok, frame = camera.read()  # read frame
    if ok:  # frame is read correctly
        frame = cv2.resize(frame, (480, 480), interpolation = cv2.INTER_AREA)
        cv2.imshow('My camera', frame)  # show frame
    if cv2.waitKey(1) == 27:  # <Escape> key
        break  # exit from cycle
camera.release()  # release web camera
cv2.destroyAllWindows()
