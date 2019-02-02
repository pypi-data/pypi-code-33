# -*- coding: utf-8 -*-

"""
A single piece of data. This interface must be implemented.
"""

from typing import Dict
from raid.data.interface.i_image_sample import IImageSample
from raid.data.interface.i_single_clf_sample import ISingleClfSample


__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ImageSingleClfSample(IImageSample, ISingleClfSample):
    def __init__(self, id: str, image_path: str, label: int, label_map: Dict[int, str]):
        IImageSample.__init__(self, image_path)
        ISingleClfSample.__init__(self, id, label, label_map)

    def get_display_image(self):
        return self.cv_image
