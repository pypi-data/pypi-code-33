#-*- coding: utf-8 -*-
"""This module is a utility module for image preprocessing.
"""
import numpy

import cv2

import os

import sys



IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def resize_image(img, target_size, cv_interpolation = cv2.INTER_LINEAR):
    """Resizes image with specified target size and casts to float32.
    
    Arguments:
        img {ndarray} -- An opencv image array
        target_size {tuple} -- A tuple of two natural numbers. Two numbers represent the width and height, respectively. 
    
    Keyword Arguments:
        cv_interpolation {int} -- cv2 interpolation. (default: {cv2.INTER_LINEAR})
    
    Returns:
        [ndarray] -- Resized image array.
    """
    resized_img = cv2.resize(img, target_size, interpolation = cv_interpolation)
    resized_img = resized_img.astype('float32')
    return resized_img

def is_image_file(filename):
    """this function checks a file extension.
    
    Arguments:
        filename {str} -- A path of file.
    
    Returns:
        [bool] -- If an extension of the file is an image, returns True. Otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in IMAGE_EXTENSIONS

def get_current_directory_name(file_path):
    """This function returns a parent directory name of the file at the file_path.
    
    Arguments:
        file_path {str} -- A path of the file.
    
    Raises:
        ValueError -- If the file is not in a directory, then this function raises a ValueError.
    
    Returns:
        [str or unicode] -- A parent directory name.(The same as a label of the file.)
    """
    splitted_filename = None
    if sys.platform == "win32":
        splitted_filename = file_path.split('\\')
    else:
        splitted_filename = file_path.split('/')
    if len(splitted_filename) < 2:
        raise ValueError('No parent directory found. You should put your image files inside a directory name which is the same as a label of them.')
    else:
        return splitted_filename[-2]

def append_elem(path, img_list, label_list, target_size):
    """This function recursively iterates over files and directories.
    While iterating, if an image file found,
    this function appends an image as an array format to img_list and appends a label to label_list
    
    Arguments:
        path {str} -- A path of a current file or a director.
        img_list {list} -- A list of images.
        label_list {list} -- A list of labels.
        target_size {tuple} -- A tuple which specifies a target size of image array.(Image files are resized to target size.)
    """
    if os.path.isdir(path):
        child_list = os.listdir(path)
        for child in child_list:
            child_path = os.path.join(path, child)
            append_elem(child_path, img_list, label_list, target_size)
    else:
        if is_image_file(path):
            img = cv2.imread(path)
            resized_image = resize_image(img, target_size)
            label = get_current_directory_name(path)
            img_list.append(resized_image)
            label_list.append(label)

def directory_images_to_arrays(directory_path, target_size):
    """Recursively iterates over child files and directories of directory_path.
    Image files will be converted to an array of images with rescaled value.
    Parent directory names will be converted to array_of_lables.
    
    Arguments:
        directory_path {str} -- A root path of image files and directories.
        target_size {tuple} -- A tuple which specifies a target size of image array.(Image files are resized to target size.)
    
    Returns:
        array_of_images, array_of_labels [(ndarray, ndarray)] --
            array_of_images is a rescaled array of resized images.
            array_of_labels is a label array of images.
            You can find a label of an image at the same index of array_of_labels.
    """
    img_list = list()
    label_list = list()
    append_elem(directory_path, img_list, label_list, target_size)
    array_of_images = numpy.asarray(img_list)
    array_of_images /= 255
    array_of_labels = numpy.asarray(label_list)
    return array_of_images, array_of_labels