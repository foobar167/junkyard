# -*- coding: utf-8 -*-
import cv2  # import OpenCV 3 with *CONTRIBUTIONS*
import copy
import random
import numpy as np

from .logic_logger import logging


class Filters:
    """ OpenCV filters """
    def __init__(self, master, filter_num=0):
        """ Initialize filters """
        self.current_filter = filter_num  # current OpenCV filter_num
        self.master = master  # link to the main GUI window
        self.frame = None  # current frame
        self.previous = None  # previous frame (gray or color)
        self.background_subtractor = None
        self.opt_flow = {  # container for Optical Flow algorithm
            # Parameters for Shi Tomasi corner detection
            'feature_params': dict(maxCorners=100,
                                   qualityLevel=0.3,
                                   minDistance=7,
                                   blockSize=7),
            # Parameters for Lucas Kanade optical flow
            'lk_params': dict(winSize=(15, 15),
                              maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)),
            # Create some random colors
            'color': np.random.randint(0, 255, (100, 3)),
            # Container for corner points of the previous frame
            'points': None,
            # Container for image mask
            'mask': None,
        }
        #
        self.affine_start = {  # starting rotation, shift and transformation
            'rotation': 0,
            'shift': [0, 0],
            'pointers3': np.float32([[0, 0], [400, 0], [0, 400]]),
            'pointers4': np.float32([[0, 0], [400, 0], [0, 400], [400, 400]]),
        }
        self.affine = None  # container for random affine values
        self.detector = None  # blob detector container
        #
        # Map strings to their corresponding OpenCV object tracker implementations
        self.object_trackers = {
            'csrt': cv2.TrackerCSRT_create,
            'kcf': cv2.TrackerKCF_create,
            'boosting': cv2.TrackerBoosting_create,
            'mil': cv2.TrackerMIL_create,
            'tld': cv2.TrackerTLD_create,
            'medianflow': cv2.TrackerMedianFlow_create,
            'mosse': cv2.TrackerMOSSE_create
        }
        self.tracker = None  # object tracker
        #
        # List of filters in the following format: [name, function, description]
        # Filter functions take frame, convert it and return converted image
        self.container = [
            ['Unchanged', self.filter_unchanged, 'Unchanged original image'],
            ['Canny', self.filter_canny, 'Canny edge detection'],
            ['Threshold', self.filter_threshold, 'Adaptive Gaussian threshold'],
            ['Harris', self.filter_harris, 'Harris corner detection'],
            ['SIFT', self.filter_sift, 'SIFT (Scale-Invariant Feature Transform) algorithm, patented'],
            ['SURF', self.filter_surf, 'SURF (Speeded-Up Robust Features) algorithm, patented'],
            ['ORB', self.filter_orb, 'ORB (Oriented FAST and Rotated BRIEF) algorithm, free'],
            ['BRIEF', self.filter_brief, 'BRIEF descriptors with the help of CenSurE (STAR) detector'],
            ['Contours', self.filter_contours, 'Draw contours with mean colors inside them'],
            ['SEEDS', self.filter_seeds, 'SEEDS (Superpixels Extracted via Energy-Driven Sampling) algorithm'],
            ['Blur', self.filter_blur, 'Blur (Gaussian, median, bilateral or classic)'],
            ['Motion', self.filter_motion, 'Motion detection'],
            ['Background', self.filter_background, 'Background subtractor (KNN, MOG2, MOG or GMG)'],
            ['Skin', self.filter_skin, 'Skin tones detection'],
            ['Optical Flow', self.filter_optflow, 'Lucas Kanade optical flow'],
            ['Affine1', self.filter_affine1, 'Affine random rotations and shifts'],
            ['Affine2', self.filter_affine2, 'Affine random transformations'],
            ['Perspective', self.filter_perspective, 'Perspective random transformations'],
            ['Equalize', self.filter_equalize, 'Histogram Equalization'],
            ['CLAHE', self.filter_clahe, 'CLAHE (Contrast Limited Adaptive Histogram Equalization) algorithm'],
            ['LAB', self.filter_lab, 'Increase the contrast using LAB color space and CLAHE'],
            ['Pyramid', self.filter_pyramid, 'Image pyramid'],
            ['Laplacian', self.filter_laplacian, 'Laplacian gradient filter'],
            ['Sobel X', self.filter_sobel_x, 'Sobel / Scharr vertical gradient filter'],
            ['Sobel Y', self.filter_sobel_y, 'Sobel / Scharr horizontal gradient filter'],
            ['Blobs', self.filter_blob, 'Blob detection'],
            ['First 3 bits', self.filter_3bits, 'Leave the first three bits'],
            ['Max RGB', self.filter_max_rgb, 'Max RGB filter'],
            ['Chaotic RGB', self.filter_chaotic_rgb, 'Chaotic color change of the RGB image'],
            ['Swap RGB', self.filter_swap_rgb, 'Chaotic swap of the RGB channels'],
            ['Tracker', self.filter_tracker, 'Object Tracking'],
        ]
        self.set_filter(self.current_filter)

    def get_filter(self):
        """ Get filter name """
        return self.container[self.current_filter][0]

    def set_filter(self, current):
        """ Set current filter """
        self.previous = None
        self.current_filter = current
        logging.info(f'Set filter to {self.get_filter()}')
        self.master.title('OpenCV Filtering - ' + self.container[self.current_filter][2])

    def next_filter(self):
        """ Set next OpenCV filter to the video loop """
        current = (self.current_filter + 1) % len(self.container)
        self.set_filter(current)

    def last_filter(self):
        """ Set last OpenCV filter to the video loop """
        current = (self.current_filter - 1) % len(self.container)
        self.set_filter(current)

    def get_names(self):
        """ Get list of filter names """
        return [name[0] for name in self.container]

    def convert(self, frame):
        """ Convert frame using current filter function """
        self.frame = frame
        return self.container[self.current_filter][1]()

    def filter_unchanged(self):
        """ Show unchanged frames """
        return self.frame

    def filter_canny(self):
        """ Canny edge detection """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        return cv2.Canny(gray, 50, 200)  # Canny edge detection

    def filter_threshold(self):
        """ Adaptive Gaussian threshold """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    def filter_harris(self):
        """ Harris corner detection """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        gray = np.float32(gray)  # convert to NumPy array
        # k-size parameter is odd and must be [3, 31]
        dest = cv2.cornerHarris(src=gray, blockSize=2, ksize=5, k=0.07)
        dest = cv2.dilate(dest, None)  # dilate corners for result, not important
        self.frame[dest > 0.01 * dest.max()] = [0, 0, 255]
        return self.frame

    def get_features(self, xfeatures):
        """ Keypoints / features for SIFT, SURF and ORB filters """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        keypoints, descriptor = xfeatures.detectAndCompute(gray, None)
        return cv2.drawKeypoints(image=self.frame, outImage=self.frame, keypoints=keypoints,
                                 flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))

    def filter_sift(self):
        """ Scale-Invariant Feature Transform (SIFT). It is patented and not totally free """
        try:
            return self.get_features(cv2.xfeatures2d.SIFT_create())
        except cv2.error:
            return self.frame  # return unchanged frame

    def filter_surf(self):
        """ Speeded-Up Robust Features (SURF). It is patented and not totally free """
        try:
            return self.get_features(cv2.xfeatures2d.SURF_create(4000))
        except cv2.error:
            return self.frame  # return unchanged frame

    def filter_orb(self):
        """ Oriented FAST and Rotated BRIEF (ORB). It is not patented and totally free """
        return self.get_features(cv2.ORB_create())

    def filter_brief(self):
        """ BRIEF descriptors with the help of CenSurE (STAR) detector """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        keypoints = cv2.xfeatures2d.StarDetector_create().detect(gray, None)
        keypoints, descriptor = cv2.xfeatures2d.BriefDescriptorExtractor_create().compute(gray, keypoints)
        return cv2.drawKeypoints(image=self.frame, outImage=self.frame, keypoints=keypoints,
                                 flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color=(51, 163, 236))

    def filter_contours(self):
        """ Draw contours with mean colors inside them """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to gray scale
        frame = self.frame.copy()  # make a copy
        for threshold in [15, 50, 100, 240]:  # use various thresholds
            ret, thresh = cv2.threshold(gray, threshold, 255, 0)
            # image, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                mask = np.zeros(gray.shape, np.uint8)  # create empty mask
                cv2.drawContours(mask, [contour], 0, 255, -1)  # fill mask with white color
                mean = cv2.mean(self.frame, mask=mask)  # find mean color inside mask
                cv2.drawContours(frame, [contour], 0, mean, -1)  # draw frame with masked mean color
            cv2.drawContours(frame, contours, -1, (0, 0, 0), 1)  # draw contours with black color
        return frame

    def filter_seeds(self):
        """ SEEDS (Superpixels Extracted via Energy-Driven Sampling) algorithm """
        display_mode = 1  # display mode for SEEDS algorithm
        num_superpixels = 400
        prior = 2
        num_levels = 4
        histogram_bins = 5
        num_iterations = 4

        frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2HSV)
        height, width, channels = frame.shape

        seeds = cv2.ximgproc.createSuperpixelSEEDS(
            width, height, channels, num_superpixels, num_levels, prior, histogram_bins)

        seeds.iterate(frame, num_iterations)
        mask = seeds.getLabelContourMask(False)

        if display_mode == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)  # convert back to RGB
            # Set superpixels color
            color_img = np.zeros((height, width, 3), np.uint8)
            color_img[:] = (255, 0, 0)
            # Stitch foreground & background together
            mask_inv = cv2.bitwise_not(mask)
            result_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
            result_fg = cv2.bitwise_and(color_img, color_img, mask=mask)
            result = cv2.add(result_bg, result_fg)
            return result
        elif display_mode == 1:
            labels = seeds.getLabels()  # get superpixels
            # Calculate average color of a superpixel in scikit-image library
            reshaped = frame.reshape((height * width, channels))
            frame_1d = np.reshape(labels, -1)
            uni = np.unique(frame_1d)
            mask = np.zeros(reshaped.shape)
            for i in uni:
                loc = np.where(frame_1d == i)[0]
                mask[loc, :] = np.mean(reshaped[loc, :], axis=0)
            frame = np.reshape(mask, [height, width, channels]).astype('uint8')
            return cv2.cvtColor(frame, cv2.COLOR_HSV2RGB)
        else:
            return mask

    def filter_blur(self):
        """ Blur (Gaussian, median, bilateral or classic) """
        # return cv2.GaussianBlur(self.frame, (29, 29), 0)  # Gaussian blur
        # return cv2.medianBlur(self.frame, 29)  # Median blur
        # return cv2.bilateralFilter(self.frame, 11, 80, 80)  # Bilateral filter preserves the edges
        return cv2.blur(self.frame, (29, 29))  # Blur classic

    def filter_motion(self):
        """ Motion detection """
        if self.previous is None or self.previous.shape != self.frame.shape:
            self.previous = self.frame.copy()  # remember previous frame
            return self.frame  # return unchanged frame
        gray1 = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)  # convert to grayscale
        gray2 = cv2.cvtColor(self.previous, cv2.COLOR_RGB2GRAY)
        self.previous = self.frame.copy()  # remember previous frame
        return cv2.absdiff(gray1, gray2)  # get absolute difference between two frames

    def filter_background(self):
        """ Background subtractor (KNN, MOG2, MOG or GMG) """
        kernel = None
        if self.background_subtractor is None:
            self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True,
                history=30,
                varThreshold=25)
            # self.background_subtractor = cv2.createBackgroundSubtractorKNN(detectShadows=True)
            # self.background_subtractor = cv2.bgsegm.createBackgroundSubtractorGMG()
            # self.background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
            #
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fgmask = self.background_subtractor.apply(self.frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
        return self.frame & cv2.cvtColor(fgmask, cv2.COLOR_GRAY2RGB)

    def filter_skin(self):
        """ Skin tones detection"""
        # Determine upper and lower HSV limits for skin tones
        lower = np.array([0, 100, 0], dtype='uint8')
        upper = np.array([50, 255, 255], dtype='uint8')
        # Switch to HSV
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_RGB2HSV)
        # Find mask of pixels within HSV range
        skin_mask = cv2.inRange(hsv, lower, upper)
        skin_mask = cv2.GaussianBlur(skin_mask, (9, 9), 0)  # noise suppression
        # Kernel for morphology operation
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        # CLOSE (dilate / erode)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        skin_mask = cv2.GaussianBlur(skin_mask, (9, 9), 0)  # noise suppression
        # Display only the masked pixels
        return cv2.bitwise_and(self.frame, self.frame, mask=skin_mask)

    def filter_optflow(self):
        """ Lucas Kanade optical flow """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        frame = self.frame.copy()  # copy the frame
        if self.previous is None or self.previous.shape != gray.shape:
            self.previous = gray.copy()  # save previous gray frame
            # Find new corner points of the frame
            self.opt_flow['points'] = cv2.goodFeaturesToTrack(
                gray, mask=None,
                **self.opt_flow['feature_params'])
            # Create a new mask image for drawing purposes
            self.opt_flow['mask'] = np.zeros_like(self.frame.copy())
        #
        # If motion is large this method will fail. Ignore exceptions
        try:
            # Calculate optical flow. cv2.error could happen here.
            points, st, err = cv2.calcOpticalFlowPyrLK(
                self.previous, gray,
                self.opt_flow['points'], None, **self.opt_flow['lk_params'])
            # Select good points
            good_new = points[st == 1]  # TypeError 'NoneType' could happen here
            good_old = self.opt_flow['points'][st == 1]
            # Draw the tracks
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                # Draw lines in the mask
                self.opt_flow['mask'] = cv2.line(self.opt_flow['mask'], (a, b), (c, d),
                                                 self.opt_flow['color'][i].tolist(), 2)
                # Draw circles in the frame
                frame = cv2.circle(frame, (a, b), 5, self.opt_flow['color'][i].tolist(), -1)
            # Update the previous frame and previous points
            self.previous = gray.copy()
            self.opt_flow['points'] = good_new.reshape(-1, 1, 2)
            return cv2.add(frame, self.opt_flow['mask'])  # concatenate frame and mask images
        except (TypeError, cv2.error):
            self.previous = None  # set optical flow to None if exception occurred
            return self.frame  # return unchanged frame when error

    def check_previous(self):
        """ Check previous frame for the 1st time """
        if self.previous is None or self.previous.shape != self.frame.shape:
            self.previous = self.frame.copy()  # remember previous frame
            self.affine = copy.deepcopy(self.affine_start)  # deep copy starting affine values

    def filter_affine1(self):
        """ Affine random rotations and shifts """
        self.check_previous()  # check previous frame for the 1st time
        self.affine['rotation'] += random.choice([-1, 1])  # random rotation (anti)clockwise
        self.affine['shift'][0] += random.choice([-1, 1])  # random shift left/right on 1 pixel
        self.affine['shift'][1] += random.choice([-1, 1])  # random shift top/bottom on 1 pixel
        rows, cols = self.frame.shape[:2]
        half_x = cols >> 1  # divide by 2 or one bit shift right
        half_y = rows >> 1
        # Do not shift too far away
        self.affine['shift'][0] = max(self.affine['shift'][0], (-half_x))
        self.affine['shift'][0] = min(self.affine['shift'][0], half_x)
        self.affine['shift'][1] = max(self.affine['shift'][1], (-half_y))
        self.affine['shift'][1] = min(self.affine['shift'][1], half_y)
        # Rotation 2D matrix
        m = cv2.getRotationMatrix2D((half_x, half_y), self.affine['rotation'], 1)
        frame = cv2.warpAffine(self.frame, m, (cols, rows))  # rotate frame
        # Shift matrix
        m = np.float32([[1, 0, self.affine['shift'][0]], [0, 1, self.affine['shift'][1]]])
        return cv2.warpAffine(frame, m, (cols, rows))  # shift frame and return it

    def filter_affine2(self):
        """ Affine random transformations """
        self.check_previous()  # check previous frame for the 1st time
        p = 'pointers3'
        for pointer in np.nditer(self.affine[p], op_flags=['readwrite']):
            pointer += random.choice([-1, 1])  # apply random shift on 1 pixel foreach element
        rows, cols = self.frame.shape[:2]  # get height and width
        m = cv2.getAffineTransform(self.affine_start[p], self.affine[p])
        return cv2.warpAffine(self.frame, m, (cols, rows))

    def filter_perspective(self):
        """ Perspective random transformations """
        self.check_previous()  # check previous frame for the 1st time
        p = 'pointers4'
        for pointer in np.nditer(self.affine[p], op_flags=['readwrite']):
            pointer += random.choice([-1, 1])  # apply random shift on 1 pixel foreach element
        rows, cols = self.frame.shape[:2]  # get height and width
        m = cv2.getPerspectiveTransform(self.affine_start[p], self.affine[p])
        return cv2.warpPerspective(self.frame, m, (cols, rows))

    def filter_equalize(self):
        """ Histogram Equalization """
        b, g, r = cv2.split(self.frame)  # split on blue, green and red channels
        b2 = cv2.equalizeHist(b)  # apply Histogram Equalization to each channel
        g2 = cv2.equalizeHist(g)
        r2 = cv2.equalizeHist(r)
        return cv2.merge((b2, g2, r2))  # merge equalized channels

    def filter_clahe(self):
        """ Contrast Limited Adaptive Histogram Equalization (CLAHE) """
        # 'clipLimit' parameter is 40 by default; 'tileGridSize' parameter is 8x8 by default
        clahe = cv2.createCLAHE(clipLimit=10., tileGridSize=(8, 8))
        b, g, r = cv2.split(self.frame)  # split on blue, green and red channels
        b2 = clahe.apply(b)  # apply CLAHE to each channel
        g2 = clahe.apply(g)
        r2 = clahe.apply(r)
        return cv2.merge((b2, g2, r2))  # merge changed channels

    def filter_lab(self):
        """ Increase the contrast using LAB color space and CLAHE """
        lab = cv2.cvtColor(self.frame, cv2.COLOR_RGB2LAB)  # convert image to LAB color model
        l, a, b = cv2.split(lab)  # split on l, a, b channels
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)  # apply CLAHE to L-channel
        lab = cv2.merge((l2, a, b))  # merge enhanced L-channel with the a and b channels
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)  # convert back to RGB and return

    def filter_pyramid(self):
        """ Image pyramid """
        frame = self.frame.copy()  # copy frame
        h, w = self.frame.shape[:2]  # get frame height and width
        x, y = int(w + (w >> 1)), 0  # 3/2 of width and 0
        image = np.zeros((h, x, 3), np.uint8)  # empty matrix filled with zeros
        image[:h, :w, :3] = self.frame  # copy frame into the matrix
        for i in range(8):  # pyramid has (8+1)=9 levels
            frame = cv2.pyrDown(frame)  # make smaller frame
            rows, cols = frame.shape[:2]
            image[y:(y + rows), w:(w + cols)] = frame  # copy smaller frame into the matrix
            y += rows  # increase vertical position of the new frame
        return image  # return image pyramid

    def filter_laplacian(self):
        """ Laplacian gradient filter """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        # return cv2.Laplacian(gray, cv2.CV_8U)
        return np.uint8(np.absolute(cv2.Laplacian(gray, cv2.CV_64F)))

    def filter_sobel_x(self):
        """ Sobel / Scharr vertical gradient filter """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        # return cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=5)
        # return np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)))
        # return np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=-1)))
        # If ksize=-1, a 3x3 Scharr filter is used which gives better results than 3x3 Sobel filter
        return cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=-1)

    def filter_sobel_y(self):
        """ Sobel / Scharr horizontal gradient filter """
        gray = cv2.cvtColor(self.frame, cv2.COLOR_RGB2GRAY)
        # return cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=5)
        # return np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)))
        # reutnr np.uint8(np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=-1)))
        # If ksize=-1, a 3x3 Scharr filter is used which gives better results than 3x3 Sobel filter
        return cv2.Sobel(gray, cv2.CV_8U, 0, 1, ksize=-1)

    def filter_blob(self):
        """ Blob detection """
        if self.detector is None:  # detect blobs for the 1st time
            # Setup SimpleBlobDetector parameters
            self.detector = []  # initialize container as a list
            params = cv2.SimpleBlobDetector_Params()
            params.minThreshold = 0
            # params.maxThreshold = 200
            params.thresholdStep = 10
            params.filterByColor = True
            params.filterByArea = True
            params.maxArea = 1000  # filter out all blobs with area > 10000 pixels
            params.minArea = 5  # filter out all blobs with area < 10 pixels
            params.filterByCircularity = True
            params.minCircularity = 0.5  # circularity of a square is 0.5
            params.minConvexity = 0.1  # convexity of a square is 0.1
            params.filterByInertia = True
            params.minInertiaRatio = 0.01  # ellipse like blob
            # Set up the detector with default parameters
            params.blobColor = 255  # extract light blobs
            self.detector.append(cv2.SimpleBlobDetector_create(params))
            params.blobColor = 0  # extract dark blobs
            self.detector.append(cv2.SimpleBlobDetector_create(params))
        # Detect blobs
        keypoints1 = self.detector[0].detect(self.frame)
        keypoints2 = self.detector[1].detect(self.frame)
        #
        # Draw detected blobs as green and blue circles
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle
        # corresponds to the size of a blob
        frame = cv2.drawKeypoints(self.frame, keypoints1, np.array([]), (255, 0, 0),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        frame = cv2.drawKeypoints(frame, keypoints2, np.array([]), (0, 0, 255),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return frame

    def filter_3bits(self):
        """ Leave the first three bits """
        bgr = (self.frame >> 5) << 5
        return bgr

    def filter_max_rgb(self):
        """ Max RGB filter: if r < m: r = 0
                            if g < m: g = 0
                            if b < m: b = 0
            if two channels have the same intensity, such as: (155, 98, 155), in this case,
            both values are kept and the smallest is reduced to zero: (155, 0, 155) """
        (b, g, r) = cv2.split(self.frame)  # split the image into its BGR components
        # Find the maximum pixel intensity values for each (x, y)-coordinate,
        # then set all pixel values less than M to zero
        m = np.maximum(np.maximum(r, g), b)
        r[r < m] = 0
        g[g < m] = 0
        b[b < m] = 0
        # Merge the channels back together and return the image
        return cv2.merge([b, g, r])

    def filter_chaotic_rgb(self):
        """ Chaotic color change of the RGB image """
        b = np.full(self.frame.shape[:-1], random.randint(-128, 128))
        g = np.full(self.frame.shape[:-1], random.randint(-128, 128))
        r = np.full(self.frame.shape[:-1], random.randint(-128, 128))
        bgr = np.int32(self.frame) + np.stack((b, g, r), axis=-1)
        bgr[bgr < 0] = 0
        bgr[bgr > 255] = 255
        return np.uint8(bgr)

    def filter_swap_rgb(self):
        """ Chaotic swap of the RGB channels """
        bgr = cv2.split(self.frame)
        random.shuffle(bgr)  # randomly shuffle color channels
        return cv2.merge(bgr)

    def filter_tracker(self):
        """ OpenCV object tracking.
            Use CSRT when you need higher object tracking accuracy and can
              tolerate slower FPS throughput.
            Use KCF when you need faster FPS throughput but can
              handle slightly lower object tracking accuracy
            Use MOSSE when you need pure speed.
            Also leave GOTURN out of the set of usable object trackers
              as it requires additional model files. """
        if self.previous is None:
            try:
                # Set initial bounding box for the object tracker
                msg = 'Select a ROI and then press SPACE or ENTER button!'
                bbox = cv2.selectROI(msg, self.frame, fromCenter=False, showCrosshair=True)
                self.tracker = self.object_trackers['csrt']()  # object tracker initialization
                self.tracker.init(self.frame, bbox)
                cv2.destroyWindow(msg)  # destroy ROI window
            except cv2.error:  # error while ROI selection
                self.previous = None
            else:
                self.previous = self.frame.copy()  # remember previous frame
        # Grab the new bounding box coordinates of the object
        success, box = self.tracker.update(self.frame)
        # Check to see if the tracking was a success
        if success:
            x, y, w, h = [int(v) for v in box]
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return self.frame
