# -*- coding: utf-8 -*-
import timeit
import numpy as np
from PIL import Image
from skimage.feature import greycomatrix

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
        array = np.array(img)  # convert PIL image to Numpy array
        r = array[:,:,0].astype(np.uint16) >> 5  # Red. Leave only 3 bit or 8 bins
        g = array[:,:,1].astype(np.uint16) >> 5  # Green
        b = array[:,:,2].astype(np.uint16) >> 5  # Blue
        rgb = (r << 6) + (g << 3) + b  # rgb color consists of 9 bit or 512 tints
        comatrix = greycomatrix(rgb, [1], [np.pi / 4], symmetric=True, levels=512)
        comatrix = np.tril(comatrix[:, :, 0, 0])  # get bottom triangle
        np.fill_diagonal(comatrix, comatrix.diagonal() >> 1)  # divide diagonal elements on 2
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
    d1 = m.descriptor(u'../doge.jpg')
    d2 = m.descriptor(u'../doge2.jpg')
    d3 = m.descriptor(u'../doge3.jpg')
    d4 = m.descriptor(u'../city.jpg')
    print(u'very small', m.distance(d1, d2))  # doge-doge2
    print(u'small', m.distance(d1, d3))  # doge-doge3
    print(u'large', m.distance(d1, d4))  # doge-city
    n = 100  # number of tests
    print(timeit.timeit(stmt=u'm.descriptor(u"../doge.jpg")', number=n,
                        setup=u'from __main__ import m') / n)
    print(timeit.timeit(stmt=u'm.distance(d1, d4)', number=n,
                        setup=u'from __main__ import m, d1, d4') / n)
