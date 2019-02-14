"""
Methods to work with images
"""

import cv2
import numpy as np
import urllib, requests
from io import BytesIO
from PIL import Image

def img_read_url(url, h = 256, w = 256, to_grey = False, timeout = 2):
    """
    Reads and preproces an image in *url* 
    
    h (float): height of the resized image
    w (float): width of the resized image.
    to_grey (bool): should the image be grey scale?
    """        
        
    resp = urllib.request.urlopen(url, timeout = timeout)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)[...,::-1]
    image = cv2.resize(image, (h, w))
    if(to_grey):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image   

def img_read_url_PIL(url, h = 256, w = 256,  timeout = 2):
    """
    Reads and preproces an image in *url* using the PIL framework
    
    h (float): height of the resized image
    w (float): width of the resized image.
    """
    
    response = requests.get(url)    
    image = Image.open(BytesIO(response.content))
    image = image.resize((h, w), Image.ANTIALIAS)
        
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
