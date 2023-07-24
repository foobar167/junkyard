import cv2
import numpy as np

from abc import ABC, abstractmethod


class FeatureExtractor(ABC):
    """ Feature extractor abstract base class (ABC) """
    def __init__(self, impath=None):
        """ Initialize abstract base class (ABC) """
        index_params = dict(algorithm=1, trees=5)  # Flann Matcher parameter
        search_params = dict(checks=50)  # Flann parameter, or pass empty dictionary instead
        self.__draw_params = dict(outImg=None, matchColor=(127, 255, 127),
                                singlePointColor=(210, 250, 250), flags=0)  # quadrilateral draw parameters
        self.__flann = cv2.FlannBasedMatcher(index_params, search_params)

        self.image, self.__keypoints, self.__descriptors, self.__pts = None, None, None, None
        image = cv2.imread(impath)  # cv2.imread function returns None if image doesn't exist
        self.set_image(image)

    @abstractmethod
    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors.
            Cannot use private '__' methods here. Only public and protected '_' methods. """
        pass

    @property
    @abstractmethod
    def name(self):
        """ Short feature extractor name for menu and config INI file """
        pass

    @property
    @abstractmethod
    def _extractor(self):
        """ Feature extractor initializer """
        pass

    @property
    def _ratio(self):
        """ Nearest neighbor matching ratio """
        return 0.70  # default value

    @property
    def _matches(self):
        return 10  # default value

    def __get_keypoints_and_descriptors(self, image):
        """ Prepare data and compute keypoints and descriptors """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # color BGR to grayscale
        keypoints, descriptors = self._detect_and_compute(gray)
        # print(len(keypoints))  # show number of keypoints, if necessary
        descriptors = np.float32(descriptors)  # convert from uint8 to float32 for FLANN matcher
        return keypoints, descriptors

    def set_image(self, image):
        """ Set current image with object to track """
        self.image = image
        if image is not None:
            self.__keypoints, self.__descriptors = self.__get_keypoints_and_descriptors(image)
            h, w = image.shape[:2]  # color image has shape [h, w, 3]
            self.__pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)

    def tracking(self, image):
        """ Draw matches between two images according to feature extractor algorithm """
        keypoints2, descriptors2 = self.__get_keypoints_and_descriptors(image)

        # Sometimes it could be a 'float NaN' descriptors - exception ValueError
        # or (-215:Assertion failed) (size_t)knn <= index_->size() - exception cv2.error
        # You can simulate this exception when wipe the web camera with a handkerchief.
        try:
            matches = self.__flann.knnMatch(self.__descriptors, descriptors2, k=2)
        except (ValueError, cv2.error):
            return self.__concat(self.image, image)

        # Store all the good matches as per David G. Lowe's ratio test
        good_matches = []
        matches_mask = np.zeros((len(matches), 2), dtype=np.int)
        for i, (m, n) in enumerate(matches):
            if m.distance < self._ratio * n.distance:
                matches_mask[i] = [1, 0]
                good_matches.append(m)

        if len(good_matches) > self._matches:  # draw a quadrilateral if there are enough matches
            src_pts = np.float32([self.__keypoints[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])
            # Find perspective transformation between two planes
            matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if matrix is not None:  # not empty
                dst = cv2.perspectiveTransform(self.__pts, matrix)  # apply perspective algorithm
                image = cv2.polylines(image, [np.int32(dst)], True, (226, 43, 138), 3)  # color (B,G,R)

        return cv2.drawMatchesKnn(self.image, self.__keypoints, image, keypoints2,
                                  matches, matchesMask=matches_mask, **self.__draw_params)

    @staticmethod
    def __concat(image1, image2):
        """ Concatenate two images """
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]
        if h1 == h2:  # if images are the same height
            return np.concatenate((image1, image2), axis=1)
        # for images with different height create an empty matrix filled with zeros
        image = np.zeros((max(h1, h2), w1+w2, 3), np.uint8)
        # combine two images
        image[:h1, :w1, :3] = image1
        image[:h2, w1:w1+w2, :3] = image2
        return image


class AKAZE(FeatureExtractor):
    """ AKAZE keypoint detector and descriptor extractor """
    name = 'AKAZE'
    _extractor = cv2.AKAZE.create()  # initiate AKAZE feature extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class KAZE(FeatureExtractor):
    """ KAZE keypoint detector and descriptor extractor """
    name = 'KAZE'
    _extractor = cv2.KAZE.create()  # initiate KAZE feature extractor
    _ratio = 0.55  # nearest neighbor matching ratio
    _matches = 4  # number of good matches to draw quadrilateral

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class ORB(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) algorithm """
    name = 'ORB'
    _extractor = cv2.ORB.create()  # init ORB feature extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class BEBLID(FeatureExtractor):
    """ BEBLID (Boosted Efficient Binary Local Image Descriptor) algorithm.
        They say it is on 14 % better than ORB. """
    name = 'BEBLID'
    _extractor = cv2.ORB.create(10000)  # init ORB feature extractor, detect a maximum of 10000 corners

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__beblid = cv2.xfeatures2d.BEBLID.create(0.75)  # the scale for the ORB keypoints is [0.75, 1.0]
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self._extractor.detect(gray, None)
        keypoints, descriptors = self.__beblid.compute(gray, keypoints)
        return keypoints, descriptors


class FastBrief(FeatureExtractor):
    """ FAST (Features from Accelerated Segment Test) and
        BRIEF (Binary Robust Independent Elementary Features) algorithms """
    name = 'FAST + BRIEF'
    _extractor = cv2.xfeatures2d.BriefDescriptorExtractor.create()  # initiate BRIEF extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__star = cv2.xfeatures2d.StarDetector.create()  # initiate FAST corner detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__star.detect(gray, None)  # find the keypoints with STAR (CenSurE) feature detector
        return self._extractor.compute(gray, keypoints)  # compute descriptors with BRIEF


class ShiTomasiBRIEF(FeatureExtractor):
    """ Shi-Tomasi Corner Detector and
        BRIEF (Binary Robust Independent Elementary Features) algorithms """
    name = 'Shi-Tomasi + BRIEF'
    _extractor = cv2.xfeatures2d.BriefDescriptorExtractor.create()  # initiate BRIEF extractor
    # _ratio = 0.7  # nearest neighbor matching ratio
    # _matches = 10  # number of good matches to draw quadrilateral

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        # Find 250 strongest corners in the image by Shi-Tomasi method
        coordinates = cv2.goodFeaturesToTrack(gray, maxCorners=250, qualityLevel=0.02, minDistance=20)
        coordinates = np.squeeze(coordinates)  # squeeze dimensions (this is a float type)
        keypoints = [cv2.KeyPoint(c[0], c[1], 13) for c in coordinates]  # convert corner coordinates to KeyPoint type
        return self._extractor.compute(gray, keypoints)  # compute descriptors with BRIEF


class HarrisBRIEF(FeatureExtractor):
    """ Harris Corner Detector and
        BRIEF (Binary Robust Independent Elementary Features) algorithms """
    name = 'Harris + BRIEF'
    _extractor = cv2.xfeatures2d.BriefDescriptorExtractor.create()  # initiate BRIEF extractor
    _ratio = 0.55  # nearest neighbor matching ratio
    # _matches = 10  # number of good matches to draw quadrilateral

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        # This filter smooths the image, reduces noise, while preserving the edges
        dst = cv2.cornerHarris(gray, blockSize=2, ksize=3, k=0.04)  # Harris corners detector
        dst = cv2.dilate(dst, None)  # dilate the result to mark the corners
        mask = np.zeros_like(gray)  # create a mask to identify corners
        mask[dst > 0.05 * dst.max()] = 255  # all pixels above a certain threshold are converted to white
        coordinates = np.argwhere(mask).astype(float)  # create an array that lists all the pixels that are corners
        keypoints = [cv2.KeyPoint(c[1], c[0], 13) for c in coordinates]  # convert corner coordinates to KeyPoint type
        return self._extractor.compute(gray, keypoints)  # compute descriptors with BRIEF
