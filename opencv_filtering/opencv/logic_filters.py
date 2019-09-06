# Application of different OpenCV filters here
import cv2  # import OpenCV 3 with *CONTRIBUTIONS*
import random
import numpy as np


class Filters():
    """ OpenCV filters """
    def __init__(self, current=0):
        """ Initialize filters """
        self.current_filter = current  # current OpenCV filter
        self.current_frame = None  # current frame
        # List of filters in the following format: [name, function, description]
        # Filter functions take frame, convert it and return converted image
        self.container = [
            ['Unchanged', self.filter_unchanged, 'Unchanged original image'],
            ['Canny', self.filter_canny, 'Canny edge detection'],
            ['Threshold', self.filter_threshold, 'Adaptive Gaussian threshold']
        ]

    def next_filter(self):
        """ Set next filter """
        self.current_filter = (self.current_filter + 1) % len(self.container)

    def last_filter(self):
        """ Set last filter """
        self.current_filter = (self.current_filter - 1) % len(self.container)

    def get_name(self):
        """ Get current filter name """
        return self.container[self.current_filter][0]  # return name from container

    def convert(self, frame):
        """ Convert frame using current filter function """
        self.current_frame = frame
        return self.container[self.current_filter][1]()

    def filter_unchanged(self):
        """ Show unchanged frames """
        return self.current_frame

    def filter_canny(self):
        """ Canny edge detection """
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)  # convert to gray scale
        return cv2.Canny(gray, 100, 200)  # Canny edge detection

    def filter_threshold(self):
        """ Adaptive Gaussian threshold """
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)  # convert to gray scale
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)


"""
camera = cv2.VideoCapture(0)  # get default camera
window_name = 'My camera'
modes = {
    '0': 'Unchanged',   # show unchanged frame
    '1': 'Canny',       # apply Canny edge detection
    '2': 'Threshold',   # adaptive Gaussian thresholding
    '3': 'Harris',      # detect corners in an image
    '4': 'SIFT',        # Scale-Invariant Feature Transform (SIFT) - patented
    '5': 'SURF',        # Speeded-Up Robust Features (SURF) - patented
    '6': 'ORB',         # Oriented FAST and Rotated BRIEF (ORB) - not patented!
    '7': 'BRIEF',       # BRIEF descriptors with the help of CenSurE (STAR) detector
    '8': 'Contours',    # Draw contours and mean colors inside contours
    '9': 'Blur',        # Blur
    'a': 'Motion',      # Motion detection
    'b': 'Background',  # Background substractor (KNN, MOG2 or GMG)
    'c': 'Skin',        # Detect skin tones
    'd': 'OptFlow',     # Lucas Kanade optical flow
    'e': 'Affine1',     # Affine random rotation and shift
    'f': 'Affine2',     # Affine random transformations
    'g': 'Perspective', # Perspective random transformations
    'h': 'Equalize',    # Histogram Equalization
    'i': 'CLAHE',       # CLAHE Contrast Limited Adaptive Histogram Equalization
    'j': 'LAB',         # Increase the contrast of an image (LAB color space + CLAHE)
    'k': 'Pyramid',     # Image pyramid
    'l': 'Laplacian',   # Laplacian gradient filter
    'm': 'Sobel X',     # Sobel / Scharr vertical gradient filter
    'n': 'Sobel Y',     # Sobel / Scharr horizontal gradient filter
    'o': 'Blobs',       # Blob detection
}
mode_unchanged   = modes['0']
mode_canny       = modes['1']
mode_threshold   = modes['2']
mode_harris      = modes['3']
mode_sift        = modes['4']
mode_surf        = modes['5']
mode_orb         = modes['6']
mode_brief       = modes['7']
mode_contours    = modes['8']
mode_blur        = modes['9']
mode_motion      = modes['a']
mode_bground     = modes['b']
mode_skin        = modes['c']
mode_optflow     = modes['d']
mode_affine1     = modes['e']
mode_affine2     = modes['f']
mode_perspective = modes['g']
mode_equalize    = modes['h']
mode_clahe       = modes['i']
mode_lab         = modes['j']
mode_pyramid     = modes['k']
mode_laplacian   = modes['l']
mode_sobelx      = modes['m']
mode_sobely      = modes['n']
mode_blobs       = modes['o']

mode = mode_canny  # default mode
algorithms = {
    mode_sift:  cv2.xfeatures2d.SIFT_create(),
    mode_surf:  cv2.xfeatures2d.SURF_create(4000),
    mode_orb:   cv2.ORB_create(),
    mode_brief: [cv2.xfeatures2d.StarDetector_create(),
                 cv2.xfeatures2d.BriefDescriptorExtractor_create()]
}
bs = None
old_gray = None
rotation = 0
shift = [0, 0]
ptrs1 = np.float32([[0,0],[400,0],[0,400]])
ptrs2 = np.copy(ptrs1)
ptrs3 = np.float32([[0,0],[400,0],[0,400],[400,400]])
ptrs4 = np.copy(ptrs3)
detector1 = None

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
        #frame = cv2.GaussianBlur(frame, (29, 29), 0)  # Gaussian blur
        #frame = cv2.blur(frame, (29, 29))  # Blur
        #frame = cv2.medianBlur(frame, 29)  # Median blur
        frame = cv2.bilateralFilter(frame, 11, 80, 80)  # Bilateral filter preserves the edges
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
    if mode == mode_optflow:
        if old_gray is None:
            # params for ShiTomasi corner detection
            feature_params = dict(maxCorners=100,
                                  qualityLevel=0.3,
                                  minDistance=7,
                                  blockSize=7)
            # Parameters for lucas kanade optical flow
            lk_params = dict(winSize=(15, 15),
                             maxLevel=2,
                             criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
            # Create some random colors
            color = np.random.randint(0, 255, (100, 3))
            # Take first frame and find corners in it
            old_frame = frame.copy()
            old_gray = gray.copy()
            ret, frame = camera.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
            # Create a mask image for drawing purposes
            mask = np.zeros_like(old_frame)
        try:  # If motion is large this method will fail. Ignore exceptions
            # calculate optical flow
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, gray, p0, None, **lk_params)
            # Select good points
            good_new = p1[st == 1]
            good_old = p0[st == 1]
            # draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
                frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
            frame = cv2.add(frame, mask)
            # Now update the previous frame and previous points
            old_gray = gray.copy()
            p0 = good_new.reshape(-1, 1, 2)
        except:
            old_gray = None  # set optical flow to None if exception occurred
    if mode == mode_affine1:
        rotation += random.choice([-1, 1])  # random rotation anticlockwise/clockwise
        shift[0] += random.choice([-1, 1])  # random shift left/right on 1 pixel
        shift[1] += random.choice([-1, 1])  # random shift up/bottom on 1 pixel
        rows, cols = frame.shape[:2]
        m = cv2.getRotationMatrix2D((cols/2, rows/2), rotation, 1)  # rotation matrix
        frame = cv2.warpAffine(frame, m, (cols, rows))
        m = np.float32([[1, 0, shift[0]], [0, 1, shift[1]]])  # translation matrix
        frame = cv2.warpAffine(frame, m, (cols, rows))
    if mode == mode_affine2:
        for ptr in np.nditer(ptrs2, op_flags=['readwrite']):
            ptr += random.choice([-1, 1])  # apply random shift on 1 pixel foreach element
        rows, cols = frame.shape[:2]
        m = cv2.getAffineTransform(ptrs1, ptrs2)
        frame = cv2.warpAffine(frame, m, (cols, rows))
    if mode == mode_perspective:
        for ptr in np.nditer(ptrs4, op_flags=['readwrite']):
            ptr += random.choice([-1, 1])  # apply random shift on 1 pixel foreach element
        rows, cols = frame.shape[:2]
        m = cv2.getPerspectiveTransform(ptrs3, ptrs4)
        frame = cv2.warpPerspective(frame, m, (cols, rows))
    if mode == mode_equalize:
        b, g, r = cv2.split(frame)  # split on blue, green and red channels
        b2 = cv2.equalizeHist(b)  # apply Histogram Equalization to each channel
        g2 = cv2.equalizeHist(g)
        r2 = cv2.equalizeHist(r)
        frame = cv2.merge((b2,g2,r2))  # merge changed channels to the current frame
    if mode == mode_clahe:
        # clipLimit is 40 by default; tileSize is 8x8 by default
        clahe = cv2.createCLAHE(clipLimit=10., tileGridSize=(8,8))
        b, g, r = cv2.split(frame)  # split on blue, green and red channels
        b2 = clahe.apply(b)  # apply CLAHE to each channel
        g2 = clahe.apply(g)
        r2 = clahe.apply(r)
        frame = cv2.merge((b2, g2, r2))  # merge changed channels to the current frame
    if mode == mode_lab:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)  # convert image to LAB color model
        l, a, b = cv2.split(lab)  # split on l, a, b channels
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)  # apply CLAHE to L-channel
        lab = cv2.merge((l2,a,b))  # merge enhanced L-channel with the a and b channels
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    if mode == mode_pyramid:
        h, w = frame.shape[:2]
        x, y = 0, int(h+h/2)
        image = np.zeros((y, w, 3), np.uint8)  # empty matrix filled with zeros
        image[:h, :w, :3] = frame
        for i in range(8):
            frame = cv2.pyrDown(frame)
            h, w = frame.shape[:2]
            image[y-h:y, x:x+w] = frame
            x += w
        frame = image
    if mode == mode_laplacian:
        #frame = cv2.Laplacian(gray, cv2.CV_8U)
        frame = np.uint8(np.absolute(cv2.Laplacian(gray, cv2.CV_64F)))
    if mode == mode_sobelx:
        #frame = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=5)
        #frame = np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)))
        # If ksize=-1, a 3x3 Scharr filter is used which gives better results than 3x3 Sobel filter
        frame = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=-1)
        #frame = np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=-1)))
    if mode == mode_sobely:
        #frame = cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=5)
        #frame = np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)))
        # If ksize=-1, a 3x3 Scharr filter is used which gives better results than 3x3 Sobel filter
        frame = cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=-1)
        #frame = np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=-1)))
    if mode == mode_blobs:
        if detector1 is None:
            # Setup SimpleBlobDetector parameters
            params = cv2.SimpleBlobDetector_Params()
            params.filterByColor = True
            params.blobColor = 255  # extract light blobs
            params.filterByArea = True
            params.maxArea = 40000
            params.filterByCircularity = True
            params.minCircularity = 0.7  # circularity of a square is 0.785
            # Set up the detector with default parameters.
            detector1 = cv2.SimpleBlobDetector_create(params)
            params.blobColor = 0  # extract dark blobs
            detector2 = cv2.SimpleBlobDetector_create(params)

        # Detect blobs
        keypoints1 = detector1.detect(frame)
        keypoints2 = detector2.detect(frame)

        # Draw detected blobs as green and blue circles
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle
        # corresponds to the size of a blob
        frame2 = cv2.drawKeypoints(frame, keypoints1, np.array([]), (0, 255, 0),
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        frame = cv2.drawKeypoints(frame2, keypoints2, np.array([]), (255, 0, 0),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

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
# """
