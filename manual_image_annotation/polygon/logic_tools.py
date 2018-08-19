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
str_polygons = 'Polygons'
str_roi = 'ROI'
str_holes = 'Holes'

def open_polygons(imframe, config, path):
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
    name = os.path.basename(imframe.path)  # get filename of the image
    parser = configparser.ConfigParser()  # create config parser
    parser.optionxform = lambda option: option  # preserve case for letters
    parser.add_section(str_image)
    parser[str_image][str_name] = name
    parser[str_image][str_md5] = imframe.md5
    parser.add_section(str_polygons)
    roi = list(imframe.roi_dict.values())  # get roi list
    holes = list(imframe.hole_dict.values())  # get holes list
    parser[str_polygons][str_roi] = codecs.encode(pickle.dumps(roi), 'base64').decode()  # wrap info
    parser[str_polygons][str_holes] = codecs.encode(pickle.dumps(holes), 'base64').decode()  # wrap info
    uid = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')  # unique ID
    name += '_' + uid + '.txt'  # unique name
    path = os.path.join(config.config_dir, name)
    with open(path, 'w') as file:
        logging.info('Save polygons into: {}'.format(name))
        parser.write(file)  # save info
