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
    '4': 'SIFT',       # Scale-Invariant Feature Transform (SIFT) - patented
    '5': 'SURF',       # Speeded-Up Robust Features (SURF) - patented
    '6': 'ORB',        # Oriented FAST and Rotated BRIEF (ORB) - not patented!
    '7': 'BRIEF',      # BRIEF descriptors with the help of CenSurE (STAR) detector
    '8': 'Motion',     # Motion detection
    '9': 'Blur',       # Blur
    'a': 'Contours',   # Draw contours and mean colors inside contours
    'b': 'Background', # Background substractor (KNN, MOG2 or GMG)
    'c': 'Skin',       # Detect skin tones
}
mode_unchanged = modes['0']
mode_canny     = modes['1']
mode_threshold = modes['2']
mode_harris    = modes['3']
mode_sift      = modes['4']
mode_surf      = modes['5']
mode_orb       = modes['6']
mode_brief     = modes['7']
mode_motion    = modes['8']
mode_blur      = modes['9']
mode_contours  = modes['a']
mode_bground   = modes['b']
mode_skin      = modes['c']

mode = mode_canny  # default mode
algorithms = {
    mode_sift:  cv2.xfeatures2d.SIFT_create(),
    mode_surf:  cv2.xfeatures2d.SURF_create(4000),
    mode_orb:   cv2.ORB_create(),
    mode_brief: [cv2.xfeatures2d.StarDetector_create(),
                 cv2.xfeatures2d.BriefDescriptorExtractor_create()]
}
bs = None

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
    if mode in [mode_sift, mode_surf, mode_orb, mode_brief]:
        algorithm = algorithms[mode]
        if mode == mode_brief:
            keypoints = algorithm[0].detect(gray, None)
            keypoints, descriptor = algorithm[1].compute(gray, keypoints)
        else:
            keypoints, descriptor = algorithm.detectAndCompute(gray, None)
        frame = cv2.drawKeypoints(image=frame, outImage=frame, keypoints=keypoints,
                                  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))
    if mode == mode_motion:
        ok, frame2 = camera.read()  # read second frame
        if not ok: continue  # skip underlying part, if frame didn't read correctly
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)  # convert to grayscale
        frame = cv2.absdiff(gray, gray2)  # get absolute difference between two frames
    if mode == mode_blur:
        frame = cv2.GaussianBlur(frame, (41, 41), 0)
    if mode == mode_contours:
        frame2 = frame.copy()  # make a copy
        for threshold in [15, 50, 100, 240]:  # use various thresholds
            ret, thresh = cv2.threshold(gray, threshold, 255, 0)
            image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                mask = np.zeros(gray.shape, np.uint8)  # create empty mask
                cv2.drawContours(mask, [contour], 0, 255, -1)  # fill mask with white color
                mean = cv2.mean(frame, mask=mask)  # find mean color inside mask
                cv2.drawContours(frame2, [contour], 0, mean, -1)  # draw frame with masked mean color
            cv2.drawContours(frame2, contours, -1, (0,0,0), 1)  # draw contours with black color
        frame = frame2
    if mode == mode_bground:
        if bs is None:
            bs = cv2.createBackgroundSubtractorKNN(detectShadows=True)
        fgmask = bs.apply(frame)
        frame = frame & cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    if mode == mode_skin:
        # determine upper and lower HSV limits for (my) skin tones
        lower = np.array([0, 100, 0], dtype="uint8")
        upper = np.array([50, 255, 255], dtype="uint8")
        # switch to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # find mask of pixels within HSV range
        skinMask = cv2.inRange(hsv, lower, upper)
        # denoise
        skinMask = cv2.GaussianBlur(skinMask, (9, 9), 0)
        # kernel for morphology operation
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        # CLOSE (dilate / erode)
        skinMask = cv2.morphologyEx(skinMask, cv2.MORPH_CLOSE, kernel, iterations=3)
        # denoise the mask
        skinMask = cv2.GaussianBlur(skinMask, (9, 9), 0)
        # only display the masked pixels
        frame = cv2.bitwise_and(frame, frame, mask=skinMask)

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
