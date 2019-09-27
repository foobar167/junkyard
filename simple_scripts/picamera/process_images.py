# -*- coding: utf-8 -*-
# This script is for Raspberry Pi camera
# Process images in directory
import os
import shutil
from PIL import Image

subdirs = True  # recursively include subdirectories or not
input_dir = '../../temp/test_pictures1/'
output_dir = '../../temp/test_pictures2/'
imname = 'test'  # image name
format = 'png'  # image format

def get_files():
    """ Get all filenames """
    fnames = []  # resulting list of all files
    if subdirs:  # recursively include files from subdirectories
        for (dirpath, dirnames, filenames) in os.walk(input_dir):
            fnames.extend(map(lambda x: os.path.join(dirpath, x), filenames))
    else:  # do not recursively include files from subdirectories
        for (dirpath, dirnames, filenames) in os.walk(input_dir):
            fnames = map(lambda x: os.path.join(dirpath, x), filenames)
            break
    return fnames

def check_image(filename):
    """ Check if filename is an image """
    try:
        im = Image.open(filename)
        im.verify()  # is it an image?
        return True
    except OSError:
        return False

def get_images():
    """ Return list of image names from directory """
    images = []
    for f in get_files():
        if check_image(f):
            images.append(f)
    return images

def process_images():
    """ Process images and save them into output directory """
    images = get_images()
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)  # delete directory
    os.makedirs(output_dir)  # create directory
    n = str(len(str(len(images))))  # zero padding number
    for i, image in enumerate(images, 1):
        name = ('{imname}_{i:0' + n + '}').format(imname=imname, i=i) + '.' + format
        im = Image.open(image)
        im.save(os.path.join(output_dir, name))

def copy_images():
    """ Copy images and save them into output directory """
    images = get_images()  # get list of all images
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)  # delete directory
    os.makedirs(output_dir)  # create directory
    n = str(len(str(len(images))))  # zero padding number
    for i, image in enumerate(images, 1):
        filename, extension = os.path.splitext(image)
        name = ('{imname}_{i:0' + n + '}').format(imname=imname, i=i) + extension
        shutil.copy(image, os.path.join(output_dir, name))

#copy_images()  # just rename and copy all images
process_images()  # batch processing of images
