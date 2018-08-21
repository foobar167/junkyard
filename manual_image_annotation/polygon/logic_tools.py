# -*- coding: utf-8 -*-
import os
import codecs
import pickle
import numpy as np
import configparser

from datetime import datetime
from PIL import Image, ImageDraw
from .logic_logger import logging

str_image = 'Image'
str_name = 'Name'
str_md5 = 'MD5'
str_polygons = 'Polygons'
str_roi = 'ROI'
str_holes = 'Holes'

def roll(mask,  # image array
         rwin,  # rolling window array
         dx,  # horizontal step - number of columns
         dy):    # vertical step - number of rows
    """ Rolling window for 2D array. Return array of rolling windows """
    shape = (int((mask.shape[0] - rwin.shape[0]) / dy) + 1,) + \
            (int((mask.shape[1] - rwin.shape[1]) / dx) + 1,) + rwin.shape
    strides = (mask.strides[0] * dy, mask.strides[1] * dx,) + mask.strides
    return np.lib.stride_tricks.as_strided(mask, shape=shape, strides=strides)

def get_images(imframe, config):
    """ Get a set of small images for machine learning """
    logging.info('Apply rolling window')
    mask = Image.new('1', (imframe.imwidth, imframe.imheight), False)  # create bitwise array of False
    for roi in imframe.roi_dict.values():  # for all ROI polygons of the image
        ImageDraw.Draw(mask).polygon(roi, outline=True, fill=True)  # fill the mask
    for hole in imframe.hole_dict.values():  # for all hole polygons of the image
        ImageDraw.Draw(mask).polygon(hole, outline=False, fill=False)  # fill the mask
    mask = np.array(mask, dtype=np.bool)  # convert mask to Numpy array
    w, h = config.get_roll_size()  # get tuple (width, height) of the rolling window
    dx, dy = config.get_step_size()  # get tuple (dx, dy) of the rolling window steps
    rwin = np.full((h, w), True, dtype=np.bool)  # create rolling window
    found = np.all(np.all(roll(mask, rwin, dx, dy) == rwin, axis=2), axis=2)  # find all matches
    # Get all founded coordinates of upper left corner of rectangle
    found = np.transpose(found.nonzero()) * [dy, dx]
    uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID
    n = str(len(str(len(found))))  # zero padding number
    for i, c in enumerate(found):  # for every coordinate of upper left corner of rectangle
        im = imframe.crop((c[1], c[0], c[1]+w, c[0]+h))  # cut sub-rectangle from the image
        imname = ('{uid}_{i:0' + n + '}.png').format(uid=uid, i=i)  # create filename
        im.save(os.path.join(config.config_dir, imname))  # save image into config dir folder

def open_polygons(imframe, path):
    """ Open polygons (ROI and holes) and show them on the canvas """
    parser = configparser.ConfigParser()  # create config parser
    parser.optionxform = lambda option: option  # preserve case for letters
    parser.read(path)  # read file with polygons
    if parser[str_image][str_md5] != imframe.md5:  # check md5 sum
        raise Exception('Wrong polygons. MD5 sum of image and from selected file should be equal.')
    roi = parser[str_polygons][str_roi]  # get roi info
    roi = pickle.loads(codecs.decode(roi.encode(), 'base64'))  # unwrap roi info
    holes = parser[str_polygons][str_holes]  # get holes info
    holes = pickle.loads(codecs.decode(holes.encode(), 'base64'))  # unwrap holes info
    logging.info('Open polygons from: {}'.format(path))
    imframe.reset(roi, holes)  # clear old and draw new polygons

def save_polygons(imframe, config):
    """ Save polygons (ROI and holes) into file """
    parser = configparser.ConfigParser()  # create config parser
    parser.optionxform = lambda option: option  # preserve case for letters
    parser.add_section(str_image)
    parser[str_image][str_name] = imframe.path
    parser[str_image][str_md5] = imframe.md5
    parser.add_section(str_polygons)
    roi = list(imframe.roi_dict.values())  # get roi list
    holes = list(imframe.hole_dict.values())  # get holes list
    parser[str_polygons][str_roi] = codecs.encode(pickle.dumps(roi), 'base64').decode()  # wrap info
    parser[str_polygons][str_holes] = codecs.encode(pickle.dumps(holes), 'base64').decode()  # wrap info
    uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID
    name = os.path.basename(imframe.path)  # get filename of the image
    name += '_' + uid + '.txt'  # unique name
    path = os.path.join(config.config_dir, name)
    with open(path, 'w') as file:
        logging.info('Save polygons into: {}'.format(name))
        parser.write(file)  # save info
