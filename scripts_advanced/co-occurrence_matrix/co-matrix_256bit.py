# -*- coding: utf-8 -*-
import timeit
import numpy as np
from PIL import Image

class CoMatrix():
    ''' Co-occurrence matrix class '''
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
        array = np.array(img)  # convert PIL image to Numpy array, np.uint8
        r = array[:,:,0] >> 6  # Red. Leave 2 bit or 4 bins
        g = array[:,:,1] >> 5  # Green. Leave 3 bit or 8 bins
        b = array[:,:,2] >> 5  # Blue. Leave 3 bit or 8 bins
        rgb = (r << 6) + (g << 3) + b  # rgb color consists of 9 bit or 512 tints
        h, w = rgb.shape  # get height and width of the array
        h -= self.dy
        w -= self.dx
        mask =                           rgb[:h, :w] < rgb[self.dy:, self.dx:]
        rows = np.where(mask,            rgb[:h, :w],  rgb[self.dy:, self.dx:])
        cols = np.where(np.invert(mask), rgb[:h, :w],  rgb[self.dy:, self.dx:])
        comatrix = np.zeros((256, 256), dtype=np.uint32)  # create 256x256 matrix
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

if __name__ == u'__main__':
    m = CoMatrix(1, 1)  # take bottom right neighbour
    d1 = m.descriptor(u'../data/doge.jpg')
    d2 = m.descriptor(u'../data/doge2.jpg')
    d3 = m.descriptor(u'../data/doge3.jpg')
    d4 = m.descriptor(u'../data/city.jpg')
    print(u'very small', m.distance(d1, d2))  # doge-doge2
    print(u'small', m.distance(d1, d3))  # doge-doge3
    print(u'large', m.distance(d1, d4))  # doge-city
    n = 100  # number of tests
    print(timeit.timeit(stmt=u'm.descriptor(u"../data/doge.jpg")', number=n,
                        setup=u'from __main__ import m') / n)
    print(timeit.timeit(stmt=u'm.distance(d1, d4)', number=n,
                        setup=u'from __main__ import m, d1, d4') / n)
