"""
Methods to work with images
"""

import cv2
import numpy as np
import urllib

def img_read_url(url, h = 256, w = 256, to_grey = False):
    """
    Reads and preproces an image in *url* 
    
    h (float): height of the resized image
    w (float): width of the resized image.
    to_grey (bool): should the image be grey scale?
    """
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)[...,::-1]
    image = cv2.resize(image, (h, w))
    if(to_grey):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image   

def img_read(path, h = 256, w = 256, to_grey = False):
    """
    Reads and preproces an image in *path* 
    
    h (float): height of the resized image
    w (float): width of the resized image.
    to_grey (bool): should the image be grey scale?
    """
    image = cv2.imread(path)[...,::-1]
    image = cv2.resize(image, (h, w))
    if(to_grey):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image 

def return_image_hist(image, no_bins_per_channel = 10):
    """ 
    Returns a vector representing the distribution of colors of an image
    """
    hist_container = []
    for channel in range(3):
        hist = cv2.calcHist([image], [channel], None, [no_bins_per_channel], [0, 256])    
        hist = [x[0] for x in hist.tolist()]
        hist_container += hist
    
    return hist_container    
