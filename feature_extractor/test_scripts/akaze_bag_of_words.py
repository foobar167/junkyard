# Bag of words using AKAZE keypoints
import os

import cv2
import numpy as np
from matplotlib import pyplot as plt


def imreads(path):
    """
    This reads all the images in a given folder and returns the results
    """
    images_path = [os.path.join(path, f) for f in os.listdir(path)]
    images = []
    for image_path in images_path:
        img = cv2.imread(image_path)
        if img is not None:
            images.append(img)
    return images


imgs_path = "../data"  # directory of images

dictionary_size = 512
# Loading images
imgs_data = []
# imreads returns a list of all images in that directory
imgs = imreads(imgs_path)
for i in range(len(imgs)):
    # create a numpy to hold the histogram for each image
    imgs_data.insert(i, np.zeros((dictionary_size, 1)))


def get_descriptors(img, detector):
    # returns descriptors of an image
    return detector.detectAndCompute(img, None)[1]


# Extracting descriptors
detector = cv2.AKAZE.create()

desc = np.array([])
# desc_src_img is a list which says which image a descriptor belongs to
desc_src_img = []
for i in range(len(imgs)):
    img = imgs[i]
    descriptors = get_descriptors(img, detector)
    if len(desc) == 0:
        desc = np.array(descriptors)
    else:
        desc = np.vstack((desc, descriptors))
    # Keep track of which image a descriptor belongs to
    for j in range(len(descriptors)):
        desc_src_img.append(i)
# important, cv2.kmeans only accepts type32 descriptors
desc = np.float32(desc)

# Clustering
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.01)
flags = cv2.KMEANS_PP_CENTERS
# desc is a type32 numpy array of vstacked descriptors
compactness, labels, dictionary = cv2.kmeans(desc, dictionary_size, None, criteria, 1, flags)

# Getting histograms from labels
size = labels.shape[0] * labels.shape[1]
for i in range(size):
    label = labels[i]
    # Get this descriptors image id
    img_id = desc_src_img[i]
    # imgs_data is a list of the same size as the number of images
    data = imgs_data[img_id]
    # data is a numpy array of size (dictionary_size, 1) filled with zeros
    data[label] += 1

ax = plt.subplot(311)
ax.set_title("Histogram from labels")
ax.set_xlabel("Visual words")
ax.set_ylabel("Frequency")
ax.plot(imgs_data[0].ravel())

matcher = cv2.FlannBasedMatcher.create()
descriptors = get_descriptors(imgs[0], detector)
result = np.zeros((dictionary_size, 1), np.float32)

# flan matcher needs descriptors to be type32
# Add dictionary as trainDescriptor
matches = matcher.match(np.float32(descriptors), dictionary)
for match in matches:
    visual_word = match.trainIdx
    result[visual_word] += 1

ax = plt.subplot(313)
ax.set_title("Histogram from FLANN")
ax.set_xlabel("Visual words")
ax.set_ylabel("Frequency")
ax.plot(result.ravel())

plt.show()
