# -*- coding: utf-8 -*-

"""
A single piece of data. This interface must be implemented.
"""

import cv2
from PIL import Image

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class IImageSample:
    def __init__(self, image_path: str):
        self.image_path: str = image_path  # Path to the original image/file of the sample.

    @property
    def cv_image(self):
        """ Return the image in an OpenCV Format. """
        image = cv2.imread(self.image_path)
        return image

    @property
    def pil_image(self):
        """ Return the image in an OpenCV Format. """
        image = Image.open(self.image_path)
        return image
