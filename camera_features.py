""" Apply different filters here """
import cv2  # import OpenCV 3 module
import numpy as np

camera = cv2.VideoCapture(0)  # get default camera
window_name = 'My camera'
modes = {
    '0': 'Unchanged',  # show unchanged frame
    '1': 'Canny',      # apply Canny edge detection
    '2': 'Threshold',  # adaptive Gaussian thresholding
    '3': 'Harris',     # detect corners in an image
    '4': 'SIRF',       # Scale-Invariant Feature Transform (SIFT) - patented
    '5': 'SURF',       # Speeded-Up Robust Features (SURF) - patented
    '6': 'ORB',        # Oriented FAST and Rotated BRIEF (ORB) - not patented!
}
mode_unchanged = modes['0']
mode_canny     = modes['1']
mode_threshold = modes['2']
mode_harris    = modes['3']
mode_sirf      = modes['4']
mode_surf      = modes['5']
mode_orb       = modes['6']

mode = mode_canny  # default mode
algorithms = {
    mode_sirf: cv2.xfeatures2d.SIFT_create(),
    mode_surf: cv2.xfeatures2d.SURF_create(4000),
    mode_orb:  cv2.ORB_create()
}

while True:
    ok, frame = camera.read()  # read frame
    if not ok: continue  # skip underlying part, if frame didn't read correctly
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to grayscale

    if mode == mode_canny:
        frame = cv2.Canny(gray, 100, 200)  # Canny edge detection
    if mode == mode_threshold:
        frame = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)  # adaptive Gaussian thresholding
    if mode == mode_harris:
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray, 2, 23, 0.04)  # 3rd parameter is odd and must be [3,31]
        frame[dst > 0.01 * dst.max()] = [0, 0, 255]
    if mode in [mode_sirf, mode_surf, mode_orb]:
        algorithm = algorithms[mode]
        keypoints, descriptor = algorithm.detectAndCompute(gray, None)
        frame = cv2.drawKeypoints(image=frame, outImage=frame, keypoints=keypoints,
                                  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))

    # write text on image
    cv2.putText(frame, mode, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (51, 163, 236), 1, cv2.LINE_AA)
    cv2.imshow(window_name, frame)  # show frame
    key = cv2.waitKey(1) & 0xff  # read keystroke
    if key == 255: continue  # skip underlying part, if key hasn't been pressed
    if key == 27: break  # <Escape> key pressed, exit from cycle
    for m in modes:
        if key == ord(m): mode = modes[m]  # if key coincide, set the appropriate mode

camera.release()  # release web camera
cv2.destroyAllWindows()
