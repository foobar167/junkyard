# -*- coding: utf-8 -*-
import timeit
import numpy as np
import comatrix
from PIL import Image

class CoMatrix1():
    ''' Co-occurrence matrix class for Python '''
    def __init__(self, dx, dy):
        ''' Initialize the class. Set non-negative distance between neighbours '''
        if dx < 0 or dy < 0: raise Exception(u'Neighbour distance have to be non-negative')
        self.dx, self.dy = dx, dy  # set neighbour distance for co-occurrence matrix

    def descriptor(self, path):
        ''' Return descriptor of the image from the path or None if it is not an image.
            Descriptor consists from 3 arrays: rows, columns and non-zero values of
            co-occurrence matrix '''
        try:
            img = Image.open(path)  # open image with PIL
        except:
            print(u'This is not an image: {}'.format(path))
            return  # return None
        array = np.array(img)  # convert PIL image to Numpy array
        r = array[:,:,0].astype(np.uint16) >> 5  # Red. Leave only 3 bit or 8 bins
        g = array[:,:,1].astype(np.uint16) >> 5  # Green
        b = array[:,:,2].astype(np.uint16) >> 5  # Blue
        rgb = (r << 6) + (g << 3) + b  # rgb color consists of 9 bit or 512 tints
        h, w = rgb.shape  # get height and width of the array
        h -= self.dy
        w -= self.dx
        mask =                           rgb[:h, :w] < rgb[self.dy:, self.dx:]
        rows = np.where(mask,            rgb[:h, :w],  rgb[self.dy:, self.dx:])
        cols = np.where(np.invert(mask), rgb[:h, :w],  rgb[self.dy:, self.dx:])
        comatrix = np.zeros((512, 512), dtype=np.uint32)  # create 512x512 matrix
        np.add.at(comatrix, [rows, cols], 1)
        rows, cols = np.nonzero(comatrix)  # get non-zero rows and columns
        return rows, cols, comatrix[rows, cols]

    def distance(self, descriptor1, descriptor2):
        ''' Calculate distance between two descriptors and return it as an integer '''
        # Restore co-occurrence matrix from descriptor.
        # Cannot use np.uint32, because of subtraction of two matrices.
        comatrix1 = np.zeros((512, 512), dtype=np.int32)
        comatrix1[descriptor1[0], descriptor1[1]] = descriptor1[2]
        comatrix2 = np.zeros((512, 512), dtype=np.int32)
        comatrix2[descriptor2[0], descriptor2[1]] = descriptor2[2]
        return np.absolute(comatrix1 - comatrix2).sum()  # sum of abs linear differences

class CoMatrix2():
    ''' Co-occurrence matrix class for C '''
    def __init__(self, dx, dy):
        ''' Initialize the class. Set non-negative distance between neighbours '''
        if dx < 0 or dy < 0: raise Exception(u'Neighbour distance have to be non-negative')
        self.dx, self.dy = dx, dy  # set neighbour distance for co-occurrence matrix

    def descriptor(self, path):
        ''' Return descriptor of the image from the path or None if it is not an image.
            Descriptor consists from 3 arrays: rows, columns and non-zero values of
            co-occurrence matrix '''
        try:
            img = Image.open(path)  # open image with PIL
        except:
            print(u'This is not an image: {}'.format(path))
            return  # return None
        array = np.array(img)  # convert PIL image to Numpy array
        return comatrix.descriptor(array, self.dx, self.dy)

    def distance(self, descriptor1, descriptor2):
        ''' Calculate distance between two descriptors and return it as an integer '''
        return comatrix.distance(descriptor1, descriptor2)

if __name__ == u'__main__':
    dx = 1
    dy = 1
    data_dir = u'../../data-2/'

    m1 = CoMatrix1(dx, dy)  # take bottom right neighbour
    p1 = m1.descriptor(data_dir + u'doge.jpg')
    p2 = m1.descriptor(data_dir + u'doge2.jpg')
    p3 = m1.descriptor(data_dir + u'doge3.jpg')
    p4 = m1.descriptor(data_dir + u'city.jpg')

    m2 = CoMatrix2(dx, dy)
    c1 = m2.descriptor(data_dir + u'doge.jpg')
    c2 = m2.descriptor(data_dir + u'doge2.jpg')
    c3 = m2.descriptor(data_dir + u'doge3.jpg')
    c4 = m2.descriptor(data_dir + u'city.jpg')

    print(u'Check equality:')
    print(m1.distance(p1, p2) == m2.distance(c1, c2))
    print(m1.distance(p1, p3) == m2.distance(c1, c3))
    print(m1.distance(p1, p4) == m2.distance(c1, c4))
    print(m1.distance(p2, p3) == m2.distance(c2, c3))
    print(m1.distance(p2, p4) == m2.distance(c2, c4))
    print(m1.distance(p3, p4) == m2.distance(c3, c4))

    n = 100  # number of tests
    print(u'Python descriptor  creation   time, msec: {}'.format(
              timeit.timeit(stmt=u'm1.descriptor(u"' + data_dir + u'doge.jpg")',
              number=n, setup=u'from __main__ import m1') / n * 1000))
    print(u'Python descriptors comparison time, msec: {}'.format(
              timeit.timeit(stmt=u'm1.distance(p1, p4)',
              number=n, setup=u'from __main__ import m1, p1, p4') / n * 1000))
    print(u'C      descriptor  creation   time, msec: {}'.format(
              timeit.timeit(stmt=u'm2.descriptor(u"' + data_dir + u'doge.jpg")',
              number=n, setup=u'from __main__ import m2') / n * 1000))
    print(u'C      descriptors comparison time, msec: {}'.format(
              timeit.timeit(stmt=u'm2.distance(c1, c4)',
              number=n, setup=u'from __main__ import m2, c1, c4') / n * 1000))
