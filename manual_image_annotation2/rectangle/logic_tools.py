# -*- coding: utf-8 -*-
import os
import codecs
import pickle
import configparser

from datetime import datetime
from .logic_logger import logging

str_image = 'Image'
str_name = 'Name'
str_md5 = 'MD5'
str_figures = 'Figures'
str_roi = 'ROI'

def get_images(imframe, config):
    """ Get a set of small images for machine learning """
    logging.info('Get ROI images')
    w, h = config.get_rect_size()  # get tuple (width, height) of rectangle
    name = os.path.basename(imframe.path)[:-4]  # get filename of the image without extension
    name += '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # add date_time
    n = str(len(str(len(imframe.roi_dict))))  # zero padding number
    m = str(len(str(max(imframe.imwidth, imframe.imheight))))  # zero padding number
    # For every coordinate of upper left corner of rectangle
    for i, c in enumerate(imframe.roi_dict.values()):
        im = imframe.crop((c[0], c[1], c[0]+w, c[1]+h))  # cut sub-rectangle from the image
        imname = ('{name}_{i:0' + n +
                  '}_{c1:0'     + m +
                  '}-{c0:0'     + m +
                  '}.png').format(name=name, i=i, c0=c[0], c1=c[1])  # create filename
        im.save(os.path.join(config.config_dir, imname))  # save image into config dir folder

def open_figures(imframe, path):
    """ Open ROI figures and show them on the canvas """
    parser = configparser.ConfigParser()  # create config parser
    parser.optionxform = lambda option: option  # preserve case for letters
    parser.read(path)  # read file with ROI figures
    """
    if parser[str_image][str_md5] != imframe.md5:  # check md5 sum
        raise Exception('Wrong polygons. MD5 sum of image and from selected file should be equal.')
    """
    roi = parser[str_figures][str_roi]  # get roi info
    roi = pickle.loads(codecs.decode(roi.encode(), 'base64'))  # unwrap roi info
    logging.info('Open ROI figures from: {}'.format(path))
    imframe.reset(roi)  # clear old and draw new polygons

def save_figures(imframe, config):
    """ Save ROI figures into file """
    parser = configparser.ConfigParser()  # create config parser
    parser.optionxform = lambda option: option  # preserve case for letters
    parser.add_section(str_image)
    parser[str_image][str_name] = imframe.path
    parser[str_image][str_md5] = imframe.md5
    parser.add_section(str_figures)
    roi = list(imframe.roi_dict.values())  # get roi list
    parser[str_figures][str_roi] = codecs.encode(pickle.dumps(roi), 'base64').decode()  # wrap info
    uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID
    name = os.path.basename(imframe.path)[:-4]  # get filename of the image without extension
    name += '_' + uid + '.txt'  # unique name
    path = os.path.join(config.config_dir, name)
    with open(path, 'w') as file:
        logging.info('Save figures into: {}'.format(name))
        parser.write(file)  # save info
