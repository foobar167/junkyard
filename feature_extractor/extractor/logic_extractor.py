import cv2
import numpy as np

from abc import ABC, abstractmethod


class FeatureExtractor(ABC):
    """ Feature extractor abstract base class (ABC) """
    def __init__(self, impath=None):
        # self.extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()  # initiate BRIEF extractor
        # self.detect_and_compute = self.detect_and_compute_3
        # self.nn_match_ratio = 0.73  # nearest neighbor matching ratio
        # self.matches = 5  # number of good matches to draw quadrilateral

        # Set some constant parameters and constant variables
        self.__params = {
            'index_params': dict(algorithm=1, trees=5),  # Flann Matcher parameter
            'search_params': dict(checks=50),  # Flann parameter, or pass empty dictionary instead
            'draw_params': dict(outImg=None, matchColor=(127, 255, 127),
                                singlePointColor=(210, 250, 250), flags=0),  # quadrilateral draw parameters
        }
        self.__flann = cv2.FlannBasedMatcher(self.__params['index_params'], self.__params['search_params'])

        self.image, self.__keypoints, self.__descriptors, self.__pts = None, None, None, None
        image = cv2.imread(impath)  # return None if image doesn't exist
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
        descriptors = np.float32(descriptors)  # convert from uint8 to float32 for FLANN matcher
        return keypoints, descriptors

    def set_image(self, image):
        """ Set current image with object to track """
        self.image = image
        if image is not None:
            self.__keypoints, self.__descriptors = self.__get_keypoints_and_descriptors(image)
            h, w = image.shape[:2]  # color image has shape [h, w, 3]
            self.__pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)

    # def __detect_and_compute_3(self, gray):
    #     """ Detect keypoints and compute descriptors """
    #     corners = cv2.goodFeaturesToTrack(gray, maxCorners=250, qualityLevel=0.02, minDistance=20)
    #     corners = np.squeeze(corners).astype(int)  # squeeze dimensions and convert from float to int
    #     keypoints = [cv2.KeyPoint(c[0], c[1], 13) for c in corners]  # convert coordinates to Keypoint type
    #     return self._extractor.compute(gray, keypoints)  # compute the descriptors with BRIEF

    def tracking(self, image):
        """ Draw matches between two images according to feature extractor algorithm """
        keypoints2, descriptors2 = self.__get_keypoints_and_descriptors(image)

        # Sometimes it could be a 'float NaN' descriptors - exception ValueError
        # or (-215:Assertion failed) (size_t)knn <= index_->size() - exception cv2.error
        # You can simulate this exception when wipe the camera with a handkerchief.
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
                                  matches, matchesMask=matches_mask, **self.__params['draw_params'])

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
    _extractor = cv2.AKAZE_create()  # initiate AKAZE feature extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class KAZE(FeatureExtractor):
    """ KAZE keypoint detector and descriptor extractor """
    name = 'KAZE'
    _extractor = cv2.KAZE_create()  # initiate KAZE feature extractor
    _ratio = 0.55  # nearest neighbor matching ratio
    _matches = 4  # number of good matches to draw quadrilateral

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class ORB(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) algorithm """
    name = 'ORB'
    _extractor = cv2.ORB_create()  # initiate ORB feature extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class FastBrief(FeatureExtractor):
    """ FAST (Features from Accelerated Segment Test) and
        BRIEF (Binary Robust Independent Elementary Features) algorithms """
    name = 'FAST+BRIEF'
    _extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()  # initiate BRIEF extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        star = cv2.xfeatures2d.StarDetector_create()  # initiate FAST corner detector
        keypoints = star.detect(gray, None)  # find the keypoints with STAR (CenSurE) feature detector
        return self._extractor.compute(gray, keypoints)  # compute keypoints and descriptors with BRIEF
