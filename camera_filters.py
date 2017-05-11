""" Apply different filters here """
import cv2  # import OpenCV 3 module
import numpy as np

camera = cv2.VideoCapture(0)  # get default camera
window_name    = 'My camera'
mode_unchanged = '1'
mode_canny     = '2'
mode_adaptive  = '3'
mode_harris    = '4'
mode_sirf      = '5'
mode_surf      = '6'
mode = mode_canny  # default mode

while True:
    ok, frame = camera.read()  # read frame
    if not ok: continue  # skip underlying part, if frame didn't read correctly
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale

    if mode == mode_canny:
        frame = cv2.Canny(gray, 100, 200)  # Canny edge detection
    if mode == mode_adaptive:
        frame = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)  # adaptive Gaussian thresholding
    if mode == mode_harris:
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray, 2, 23, 0.04)  # 3rd parameter is odd and must be [3,31]
        frame[dst > 0.01 * dst.max()] = [0, 0, 255]
    if mode == mode_sirf:
        sift = cv2.xfeatures2d.SIFT_create()
        keypoints, descriptor = sift.detectAndCompute(gray, None)
        frame = cv2.drawKeypoints(image=frame, outImage=frame, keypoints=keypoints,
                                  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))
    if mode == mode_surf:
        surf = cv2.xfeatures2d.SURF_create(4000)
        keypoints, descriptor = surf.detectAndCompute(gray, None)
        frame = cv2.drawKeypoints(image=frame, outImage=frame, keypoints=keypoints,
                                  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))

    cv2.imshow(window_name, frame)  # show frame
    key = cv2.waitKey(1) & 0xff  # read keystroke
    if key == 255: continue  # skip underlying part, if key hasn't been pressed
    if key == 27: break  # <Escape> key pressed, exit from cycle
    if key == ord(mode_unchanged): mode = mode_unchanged  # show unchanged frame
    if key == ord(mode_canny):     mode = mode_canny      # apply Canny edge detection
    if key == ord(mode_adaptive):  mode = mode_adaptive   # adaptive Gaussian thresholding
    if key == ord(mode_harris):    mode = mode_harris     # detect corners in an image
    if key == ord(mode_sirf):      mode = mode_sirf       # Scale-Invariant Feature Transform (SIFT)
    if key == ord(mode_surf):      mode = mode_surf       # Speeded-Up Robust Features (SURF)

camera.release()  # release web camera
cv2.destroyAllWindows()
