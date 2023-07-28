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
        self.__frame_color = (0, 35, 255)  # (blue, green, red)
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
        matches_mask = np.zeros((len(matches), 2), dtype=np.int32)
        for i, (m, n) in enumerate(matches):
            if m.distance < self._ratio * n.distance:
                matches_mask[i] = [1, 0]
                good_matches.append(m)

        # print(len(good_matches))  # print good matches if necessary
        if len(good_matches) > self._matches:  # draw a quadrilateral if there are enough matches
            src_pts = np.float32([self.__keypoints[m.queryIdx].pt for m in good_matches])
            dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches])
            # Find perspective transformation between two planes
            matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if matrix is not None:  # not empty
                dst = cv2.perspectiveTransform(self.__pts, matrix)  # apply perspective algorithm
                image = cv2.polylines(image, [np.int32(dst)], True, self.__frame_color, 3)  # color (B,G,R)

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


class SIFT(FeatureExtractor):
    """ SIFT (Scale-Invariant Feature Transform) algorithm.
            SIFT consist of 4 main steps, which are: (1) scale space extreme detection;
            (2) key-point localization; (3) orientation assignment; (4) key-point descriptor. """
    name = 'SIFT'  # SIFT became free since March 2020, and SURF is still private
    _extractor = cv2.SIFT.create()  # initiate SIFT keypoint detector and descriptor extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class RootSIFT(FeatureExtractor):
    """ 2012 paper "Three things everyone should know to improve object retrieval"
            RootSIFT increases object recognition accuracy, quantization, and retrieval accuracy. """
    name = 'RootSIFT'
    _extractor = cv2.SIFT.create()  # initiate SIFT keypoint detector and descriptor extractor

    def compute(self, gray, keypoints, eps=1e-7):
        keypoints, descriptors = self._extractor.compute(gray, keypoints)  # compute SIFT descriptors
        if len(keypoints) == 0:   # if there are no keypoints or descriptors, return an empty tuple
            return [], None
        # Apply the Hellinger kernel by first L1-normalizing and taking the square-root
        descriptors /= (descriptors.sum(axis=1, keepdims=True) + eps)
        descriptors = np.sqrt(descriptors)
        # descriptors /= (np.linalg.norm(descriptors, axis=1, ord=2) + eps)
        return keypoints, descriptors

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self._extractor.detect(gray)  # use SIFT as keypoint detector
        return self.compute(gray, keypoints)  # return keypoints and descriptors


class BRISK(FeatureExtractor):
    """ BRISK (Binary Robust Invariant Scalable Keypoints) algorithm.
            Uses AGAST for feature detection and FAST scores as a metric.
            BRISK sampling pattern is made up of concentric circles. """
    name = 'BRISK'
    _extractor = cv2.BRISK.create()  # init BRISK keypoint detector and descriptor extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class AKAZE(FeatureExtractor):
    """ AKAZE keypoint detector and descriptor extractor.
            Faster version of KAZE detector using Fast Explicit Diffusion. """
    name = 'AKAZE'
    _extractor = cv2.AKAZE.create()  # initiate AKAZE keypoint detector and descriptor extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class KAZE(FeatureExtractor):
    """ KAZE keypoint detector and descriptor extractor.
            Points of interest as found using nonlinear diffusion filtering which preserves edges
            and improves the distinctiveness. It is computationally expensive, but it has better performance
            and a more stable repeatability score than FAST/AGAST based detectors. """
    name = 'KAZE'
    _extractor = cv2.KAZE.create(
        nOctaves=2,  # default: 4
        nOctaveLayers=4,  # default: 4
    )  # initiate KAZE keypoint detector and descriptor extractor
    _ratio = 0.55  # default: 0.7; nearest neighbor matching ratio
    _matches = 4  # default: 10; number of good matches to draw quadrilateral

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class ORB(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector and descriptor extractor.
            ORB is a mashup of FAST and BRIEF, it uses FAST for keypoint detection and a
            modified BRIEF (rBRIEF) for the descriptor which makes it rotation invariant.
            ORB is less computationally expensive than BRISK but BRISK is a much better descriptor than ORB. """
    name = 'ORB'
    _extractor = cv2.ORB.create(
        nfeatures=1000,  # default: 500; max number of features to retain
        scaleFactor=1.2,  # default: 1.2; pyramid decimation ratio
        nlevels=12,  # default: 8; number of pyramid levels, more layers for small objects
        # The size of the border where the features are not detected. It should roughly match the patchSize parameter.
        edgeThreshold=20,  # default: 31
        # The level of pyramid to put source image to. Previous layers are filled with upscaled source image.
        firstLevel=0,  # default: 0
        # The number of points that produce each element of the oriented BRIEF descriptor.
        WTA_K=2,  # default: 2; could be (2,3,4)
        # cv2.ORB_FAST_SCORE produces slightly less stable keypoints, but it is a little faster to compute.
        scoreType=cv2.ORB_HARRIS_SCORE,  # default: cv2.ORB_HARRIS_SCORE. Alternative is cv2.ORB_FAST_SCORE
        patchSize=31,  # default: 31; size of the patch used by the oriented BRIEF descriptor
        fastThreshold=0,  # default: 20
    )  # init ORB

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        return self._extractor.detectAndCompute(gray, None)  # return keypoints and descriptors


class MSDDetectorFREAK(FeatureExtractor):
    """ MSDDetector (Maximal Self-Dissimilarity) keypoint detector.
            Self Similarity can be defined as the set of distances of a patch to those located in its
            surroundings, with distances usually measured through the Sum of Squared Distances.
            Whenever the task mandates looking for large rather than small minima over such distances,
            we will use the term self-dissimilarity.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'MSDDetector + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.xfeatures2d.MSDDetector.create(
            m_patch_radius=3,  # default: 3
            m_search_area_radius=3,  # default: 5
            m_nms_radius=2,  # default: 5
            # this parameter does not work: m_nms_scale_radius=0,
            m_th_saliency=200.0,  # default: 250.0
            m_kNN=5,  # default: 4
            m_scale_factor=1.15,  # default: 1.25; VERY effective, but slow
            m_n_scales=-1,  # default: -1
            m_compute_orientation=False,  # default: False
        )  # initiate MSDDetector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)  # find keypoints with MSDDetector
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbTeblid(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        TEBLID (Triplet-based Efficient Binary Local Image Descriptor) descriptor extractor.
            It is an improvement over BEBLID, that uses triplet loss, hard negative mining,
            and anchor swap to improve the image matching results. """
    name = 'ORB + TEBLID'
    _extractor = cv2.xfeatures2d.TEBLID.create(
        scale_factor=0.75,  # 0.75 for ORB, 5.00 for StarDetector
    )  # init TEBLID descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=4000,  # default: 500
        )  # init ORB
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbBeblid(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        BEBLID (Boosted Efficient Binary Local Image Descriptor) descriptor extractor.
            They say it is on 14 % better than ORB descriptor extractor.
         """
    name = 'ORB + BEBLID'
    _extractor = cv2.xfeatures2d.BEBLID.create(
        scale_factor=0.75,  # the scale for the ORB keypoints is [0.75, 1.0]
    )  # init BEBLID

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=4000,  # default: 500
        )  # init ORB
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        keypoints, descriptors = self._extractor.compute(gray, keypoints)
        return keypoints, descriptors


class HarrisLaplaceFREAK(FeatureExtractor):
    """ Harris-Laplace - Gradient based corner detection. Harris detector gives the position
            and orientation of a corner, convolution with Laplacian function gives the
            size of area of interest near the corner.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'HarrisLaplace + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.xfeatures2d.HarrisLaplaceFeatureDetector.create()  # init Harris-Laplace
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbVgg(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        VGG (Oxford Visual Geometry Group) descriptor trained end to end using
            "Descriptor Learning Using Convex Optimisation" (DLCO) aparatus described in
            paper of K. Simonyan, A. Vedaldi, and A. Zisserman.
            Learning local feature descriptors using convex optimisation.
            IEEE Transactions on Pattern Analysis and Machine Intelligence, 2014. """
    name = 'ORB + VGG'
    _extractor = cv2.xfeatures2d.VGG.create(
        scale_factor=0.75  # default: 6.25
    )  # init VGG descriptor extractor
    # _ratio = 0.7  # default: 0.7; nearest neighbor matching ratio
    _matches = 4  # default: 10; number of good matches to draw quadrilateral

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=400,  # default: 500
        )  # init ORB detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class TbmrFreak(FeatureExtractor):
    """ TBMR (Tree-Based Morse Regions) feature detector.
            This algorithm is based on Component Tree (Min/Max) as well as MSER,
            but uses a Morse-theory approach to extract features. Features are ellipses (similar to MSER,
            however a MSER feature can never be a TBMR feature and vice versa).
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'TBMR + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.xfeatures2d.TBMR.create()  # initiate TBMR
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class StarDetectorFREAK(FeatureExtractor):
    """ StarDetector keypoint detector.
            It uses a bi-level approximation of the Laplacian Of Gaussian(LOG) filter.
        FREAK (Fast Retina Keypoint) descriptor extractor.
            A cascade of binary strings is computed by efficiently comparing image intensities
            over a retinal sampling pattern. """
    name = 'StarDetector + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.xfeatures2d.StarDetector.create()  # initiate StarDetector keypoint detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbBoostDesc(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        BoostDesc (Learning Image Descriptors with Boosting) described in papers:
            'Boosting binary keypoint descriptors' and 'Learning image descriptors with boosting'. """
    name = 'ORB + BoostDesc'
    _extractor = cv2.xfeatures2d.BoostDesc.create(
        desc=200,  # default: 302; could be (100, 101, 102, 200, 300, 301, 302)
        scale_factor=0.75  # default: 6.25
    )  # init BoostDesc descriptor extractor
    _matches = 6  # default: 10; number of good matches to draw quadrilateral

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=400,  # default: 500
        )  # init ORB detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class SimpleBlobDetectorFREAK(FeatureExtractor):
    """ SimpleBlobDetector is used to detect blobs and filter them based on different characteristics.
            It uses thresholding, grouping and merging of blobs to determine relevant features.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'BlobDetector + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor
    _matches = 6  # default: 10; number of good matches to draw quadrilateral

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        params = cv2.SimpleBlobDetector.Params()  # setup SimpleBlobDetector parameters
        # Change thresholds
        params.minThreshold = 0  # default: 50
        params.maxThreshold = 255  # default: 220
        params.thresholdStep = 9  # default: 10; step size to go from minThreshold to maxThreshold
        # The number of threshold values a blob has to be detected at to be considered stable.
        params.minRepeatability = 2  # default: 2
        # A numeric value representing the minimum distance in pixels between pixel group centers from
        # several binary (thresholded) images above which they are considered as distinct blobs.
        params.minDistBetweenBlobs = 1  # default: 10
        # Filter by Area. Whether blobs should be filtered based on their area in pixels.
        params.filterByArea = True  # default: True
        params.minArea = 20  # default: 25; blobs smaller than this value in pixels are discarded
        params.maxArea = 5000  # default: 5000; blobs larger than this value in pixels are discarded
        # Filter by Color. Whether blobs should be filtered based on color.
        params.filterByColor = False  # default: True
        # 0 will select dark blobs, 255 will select bright blobs.
        params.blobColor = 0  # default: 0
        # Filter by Circularity. Whether blobs should be filtered based on circularity.
        params.filterByCircularity = False  # default: False
        # Blobs with smaller circularity than this value are discarded.
        params.minCircularity = 0.1  # default: 0.8
        params.maxCircularity = float('inf')  # default: Inf
        # Filter by Convexity. Whether blobs should be filtered based on convexity.
        params.filterByConvexity = False  # default: True
        params.minConvexity = 0.001  # default: 0.95
        params.maxConvexity = float('inf')  # default: Inf
        # Filter by Inertia. Whether blobs should be filtered based on their inertia ratio.
        params.filterByInertia = False  # default: True
        params.minInertiaRatio = 0.1  # default: 0.1
        params.maxInertiaRatio = float('inf')  # default: Inf
        #
        self.__detector = cv2.SimpleBlobDetector.create(params)  # initiate SimpleBlobDetector with the parameters
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class SiftDaisy(FeatureExtractor):
    """ SIFT (Scale-Invariant Feature Transform) algorithm.
        DAISY (A Fast Local Descriptor for Dense Matching) descriptor extractor.
            DAISY is designed for dense point matching,
            which means it computes a descriptor for every pixel in the image. """
    name = 'SIFT + DAISY'
    _extractor = cv2.xfeatures2d.DAISY.create(
        use_orientation=True,  # default: False; True - for orientation invariance
    )  # init DAISY descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.SIFT.create()  # init SIFT detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class StarDetectorDAISY(FeatureExtractor):
    """ StarDetector keypoint detector.
        DAISY (A Fast Local Descriptor for Dense Matching) descriptor extractor.
            DAISY is designed for dense point matching,
            which means it computes a descriptor for every pixel in the image. """
    name = 'StarDetector + DAISY'
    _extractor = cv2.xfeatures2d.DAISY.create()  # init DAISY descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.xfeatures2d.StarDetector.create()  # initiate StarDetector keypoint detector
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class MserFreak(FeatureExtractor):
    """ MSER (Maximally Stable Extremal Region extractor) detector of regions.
            MSER is used for images that have uniform regions separated by strong intensity changes.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'MSER + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.MSER.create()  # MSER is for detecting regions but can be used to find keypoints
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbBrief(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        BRIEF (Binary Robust Independent Elementary Features) is a fast feature descriptor
            (not a feature detector). """
    name = 'ORB + BRIEF'
    _extractor = cv2.xfeatures2d.BriefDescriptorExtractor.create(
        use_orientation=True,  # default: False; - True for rotation invariance
    )  # init BRIEF

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=2500,  # default: 500
        )  # init ORB
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class AgastFreak(FeatureExtractor):
    """ FAST (Features from Accelerated Segment Test) keypoint detector.
        AGAST descriptor extractor is a faster version of FAST feature detector. """
    name = 'AGAST + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor
    _ratio = 0.65  # default: 0.7; nearest neighbor matching ratio
    _matches = 10  # default: 10; number of good matches to draw quadrilateral

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.AgastFeatureDetector.create(
            threshold=14,  # default: 10
        )  # initiate AGAST keypoint detector
        # self.__fast.setNonmaxSuppression(0)  # disable nonmaxSuppression (more keypoints, slower)
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)  # find keypoints
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class FastFreak(FeatureExtractor):
    """ FAST (Features from Accelerated Segment Test) keypoint detector.
            FAST - circular template based corner feature detector.
            A point is considered a corner only if a there is a certain number of contiguous pixels
            in the circle which are lighter/darker than the center pixel.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'FAST + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor
    _ratio = 0.65  # default: 0.7; nearest neighbor matching ratio
    _matches = 10  # default: 10; number of good matches to draw quadrilateral

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.FastFeatureDetector.create(
            threshold=14,  # default: 10
        )  # initiate FAST keypoint detector
        # self.__fast.setNonmaxSuppression(0)  # disable nonmaxSuppression (more keypoints, slower)
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)  # find keypoints
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class GFTTDetectorFREAK(FeatureExtractor):
    """ GFTTDetector (Good Features To Track Detector) detects corners using a combination of two algorithms:
            Harris and GFTT. It makes use of local auto-correlation function
            with respect to the intensity of the image.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'GFTT + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.GFTTDetector.create()  # initiate GFTT
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class ShiTomasiFREAK(FeatureExtractor):
    """ Shi-Tomasi Corner Detector.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'Shi-Tomasi + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        # Find 500 strongest corners in the image by Shi-Tomasi method
        coordinates = cv2.goodFeaturesToTrack(gray, maxCorners=1000, qualityLevel=0.02, minDistance=20)
        coordinates = np.squeeze(coordinates)  # squeeze dimensions (this is a float type)
        keypoints = [cv2.KeyPoint(c[0], c[1], 13) for c in coordinates]  # convert corner coordinates to KeyPoint type
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class OrbLatch(FeatureExtractor):
    """ ORB (Oriented FAST and Rotated BRIEF) keypoint detector.
        LATCH (Learned Arrangements of Three Patch Codes) binary descriptor
        based on learned comparisons of triplets of image patches.
            It is a binary descriptor that uses 3×3 patches for comparison.
            LATCH elects 3 patches, the first of which is named anchor, and then calculates the
            Frobenius distance between an anchor and the other 2 pixels.
            After that, it compares both distances, learned and selects the best patch triples. """
    name = 'ORB + LATCH'
    _extractor = cv2.xfeatures2d.LATCH.create()  # init LATCH descriptor extractor

    def __init__(self, impath=None):
        """ Set additional variables to the child class """
        self.__detector = cv2.ORB.create(
            nfeatures=2000,  # default: 500
        )  # init ORB
        # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
        super().__init__(impath)  # add a call to the parent's __init__() function

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        keypoints = self.__detector.detect(gray, None)
        return self._extractor.compute(gray, keypoints)  # compute descriptors


class HarrisFREAK(FeatureExtractor):
    """ Harris Corner Detector.
        FREAK (Fast Retina Keypoint) descriptor extractor. """
    name = 'Harris + FREAK'
    _extractor = cv2.xfeatures2d.FREAK.create()  # init FREAK descriptor extractor
    _ratio = 0.55  # default: 0.7; nearest neighbor matching ratio

    def _detect_and_compute(self, gray):
        """ Detect keypoints and compute descriptors """
        # This filter smooths the image, reduces noise, while preserving the edges
        dst = cv2.cornerHarris(
            gray,
            blockSize=2,  # neighborhood size (see the details on cornerEigenValsAndVecs )
            ksize=5,  # aperture parameter for the Sobel operator
            k=0.07,  # Harris detector free parameter
        )  # Harris corners detector
        dst = cv2.dilate(dst, None)  # dilate the result to mark the corners
        mask = np.zeros_like(gray)  # create a mask to identify corners
        mask[dst > 0.2 * dst.max()] = 255  # all pixels above a certain threshold are converted to white
        coordinates = np.argwhere(mask).astype(float)  # create an array that lists all the pixels that are corners
        keypoints = [cv2.KeyPoint(c[1], c[0], 13) for c in coordinates]  # convert corner coordinates to KeyPoint type
        return self._extractor.compute(gray, keypoints)  # compute descriptors with BRIEF


# class StarDetectorLUCID(FeatureExtractor):
#     """ StarDetector keypoint detector. LUCID descriptor extractor.
#         DOES NOT WORK! Commented for now.
#           LUCID (Locally Uniform Comparison Image Descriptor) is based on the linear time permutation distance
#           among RGB ordered value of two image patches.
#           LUCID uses Hamming distance as a comparing method in the matching stage. """
#     name = 'StarDetector + LUCID'
#     _extractor = cv2.xfeatures2d.LUCID.create()  # init LUCID descriptor extractor
#
#     def __init__(self, impath=None):
#         """ Set additional variables to the child class """
#         self.__detector = cv2.xfeatures2d.StarDetector.create()  # initiate StarDetector keypoint detector
#         # Initialize all variables BEFORE super() function. Otherwise, there will be an error.
#         super().__init__(impath)  # add a call to the parent's __init__() function
#
#     def _detect_and_compute(self, gray):
#         """ Detect keypoints and compute descriptors """
#         keypoints = self.__detector.detect(gray, None)
#         # Use color image, gray image throws error:
#         # (-215:Assertion failed) _src.channels() == 3 in function 'cv::xfeatures2d::LUCIDImpl::compute'
#         return self._extractor.compute(self.image, keypoints)  # compute descriptors


# SURF is a private algorithm, so it is excluded from OpenCV library.
#     SURF (Speed-Up Robust Feature) is computationally faster than SIFT,
#     and it is robust against image transformation and noise.
#     It consists of two major steps: (1) Key point detection; (2) key point description.
