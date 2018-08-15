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

    def comatrix(self, path):
        ''' Return co-occurrence matrix of the image or None if it is not an image '''
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
        # Cannot use np.uint32, because of subtraction of two matrices.
        comatrix = np.zeros((512, 512), dtype=np.int32)  # create 512x512 matrix
        np.add.at(comatrix, [rows, cols], 1)
        return comatrix

    def distance(self, comatrix1, comatrix2):
        ''' Calculate distance between two co-occurrence matrices
            and return it as an integer '''
        return np.absolute(comatrix1 - comatrix2).sum()  # sum of abs linear differences

if __name__ == u'__main__':
    m = CoMatrix(1, 1)  # take bottom right neighbour
    d1 = m.comatrix(u'../data/doge.jpg')
    d2 = m.comatrix(u'../data/doge2.jpg')
    d3 = m.comatrix(u'../data/doge3.jpg')
    d4 = m.comatrix(u'../data/city.jpg')
    print(u'very small', m.distance(d1, d2))  # doge-doge2
    print(u'small', m.distance(d1, d3))  # doge-doge3
    print(u'large', m.distance(d1, d4))  # doge-city
    n = 100  # number of tests
    print(timeit.timeit(stmt=u'm.comatrix(u"../data/doge.jpg")', number=n,
                        setup=u'from __main__ import m') / n)
    print(timeit.timeit(stmt=u'm.distance(d1, d4)', number=n,
                        setup=u'from __main__ import m, d1, d4') / n)
