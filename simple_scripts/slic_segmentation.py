# SLIC (Simple Linear Iterative Clustering) segmentation algorithm.
# Original link: https://stackoverflow.com/a/57746835/7550928
import numpy as np
import cv2
from skimage import segmentation
from skimage.segmentation import mark_boundaries
from skimage.data import astronaut


def slic_segmentation(image, segments):
    """ Calculate average color of a superpixel in scikit-image library """
    reshaped = image.reshape((image.shape[0]*image.shape[1], image.shape[2]))
    slic_1d = np.reshape(segments, -1)
    uni = np.unique(slic_1d)
    mask = np.zeros(reshaped.shape)
    for i in uni:
        loc = np.where(slic_1d==i)[0]
        mask[loc, :] = np.mean(reshaped[loc, :], axis=0)
    return np.reshape(mask, [image.shape[0], image.shape[1], image.shape[2]]).astype('uint8')


input = cv2.cvtColor(astronaut(), cv2.COLOR_BGR2RGB)
segments = segmentation.slic(input, compactness=10, n_segments=1000, sigma=3)
output = slic_segmentation(input, segments)

cv2.imshow('Original image', input)
cv2.imshow('SLIC segmentation', output)
cv2.imshow('With boundaries', mark_boundaries(input, segments))

cv2.waitKey(0)  # press any key to close the window
cv2.destroyAllWindows()


if __name__ == '__main__':
    def nothing(*arg):
        pass

    cv2.namedWindow('SEEDS')
    cv2.createTrackbar('Number of Superpixels', 'SEEDS', 400, 1000, nothing)
    cv2.createTrackbar('Iterations', 'SEEDS', 4, 12, nothing)

    seeds = None
    display_mode = 0
    num_superpixels = 400
    prior = 2
    num_levels = 4
    num_histogram_bins = 5

    cap = cv2.VideoCapture(0)  # get default camera
    while True:
        flag, img = cap.read()
        converted_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        height, width, channels = converted_img.shape
        num_superpixels_new = cv2.getTrackbarPos('Number of Superpixels', 'SEEDS')
        num_iterations = cv2.getTrackbarPos('Iterations', 'SEEDS')

        if not seeds or num_superpixels_new != num_superpixels:
            num_superpixels = num_superpixels_new

        seeds = cv2.ximgproc.createSuperpixelSEEDS(
            width, height, channels, num_superpixels, num_levels, prior, num_histogram_bins)

        color_img = np.zeros((height, width, 3), np.uint8)
        color_img[:] = (0, 0, 255)
        seeds.iterate(converted_img, num_iterations)
        mask = seeds.getLabelContourMask(False)

        if display_mode == 0:
            # Stitch foreground & background together
            mask_inv = cv2.bitwise_not(mask)
            result_bg = cv2.bitwise_and(img, img, mask=mask_inv)
            result_fg = cv2.bitwise_and(color_img, color_img, mask=mask)
            result = cv2.add(result_bg, result_fg)
            cv2.imshow('SEEDS', result)
        elif display_mode == 1:
            labels = seeds.getLabels()
            segments = slic_segmentation(img, labels)
            cv2.imshow('SEEDS', segments)
        else:
            cv2.imshow('SEEDS', mask)

        ch = cv2.waitKey(1)
        if ch == 27:
            break
        elif ch & 0xff == ord(' '):
            display_mode = (display_mode + 1) % 3
    cv2.destroyAllWindows()


    def nothing(*arg):
        pass

    cv2.namedWindow('SLIC')
    cv2.createTrackbar('Region Size', 'SLIC', 32, 100, nothing)

    seeds = None
    display_mode = 0
    region_size = 32

    cap = cv2.VideoCapture(0)  # get default camera
    while True:
        flag, img = cap.read()
        converted_img = cv2.GaussianBlur(img, (5, 5), 0)  # gaussian blur
        converted_img = cv2.cvtColor(converted_img, cv2.COLOR_BGR2LAB)  # convert to LAB
        height, width, channels = converted_img.shape
        region_size_new = cv2.getTrackbarPos('Region Size', 'SLIC')

        if not seeds or region_size_new != region_size:
            region_size = region_size_new

        seeds = cv_slic = cv2.ximgproc.createSuperpixelSLIC(
            converted_img, algorithm=cv2.ximgproc.SLICO, region_size=region_size)

        color_img = np.zeros((height, width, 3), np.uint8)
        color_img[:] = (0, 0, 255)
        seeds.iterate()
        mask = seeds.getLabelContourMask(False)

        # Stitch foreground & background together
        mask_inv = cv2.bitwise_not(mask)
        result_bg = cv2.bitwise_and(img, img, mask=mask_inv)
        result_fg = cv2.bitwise_and(color_img, color_img, mask=mask)
        result = cv2.add(result_bg, result_fg)

        if display_mode == 0:
            cv2.imshow('SLIC', result)
        else:
            cv2.imshow('SLIC', mask)

        ch = cv2.waitKey(1)
        if ch == 27:
            break
        elif ch & 0xff == ord(' '):
            display_mode = (display_mode + 1) % 2
    cv2.destroyAllWindows()
