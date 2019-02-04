# -*- coding: utf-8 -*-

"""
A single piece of data. This interface must be implemented.
"""

from typing import Dict

import cv2
from k_util import Region
from k_vision import visual, text

from raid.data.interface.i_image_sample import IImageSample
from raid.data.interface.i_single_clf_sample import ISingleClfSample
import numpy as np

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ImageSingleClfSample(IImageSample, ISingleClfSample):
    def __init__(self, id: str, image_path: str, label: int, label_map: Dict[int, str]):
        IImageSample.__init__(self, image_path)
        ISingleClfSample.__init__(self, id, label, label_map)

    def get_display_image(self):
        return self.cv_image

    def get_prediction_image(self, p=None):

        # Safely cast to list.
        if type(p) is int:
            p = [p]

        label_width = 80
        size = (48, 48)
        label_height = size[1] // 2

        image = cv2.resize(self.cv_image, size)
        canvas_width = size[1] + label_width
        canvas_height = size[0]
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

        canvas = visual.safe_implant(canvas, image, 0, size[1], 0, size[0])

        truth_label = " ".join(self.semantic_labels)
        canvas = text.write_into_region(
            canvas, truth_label, Region(size[1], size[1] + label_width, 0, label_height),
            color=(200, 200, 200),
            font_size=12,
            h_align=text.ALIGN_RIGHT,
            bg_color=(30, 30, 30)

        )

        prediction_label = " ".join(self.get_semantic_labels(p))
        correct = not set(p).isdisjoint(self.labels)
        color = (0, 255, 0) if correct else (0, 0, 255)
        canvas = text.write_into_region(
            canvas, prediction_label, Region(size[1], size[1] + label_width, label_height, label_height * 2),
            color=color,
            font_size=12,
            h_align=text.ALIGN_RIGHT,
            bg_color=(30, 30, 30)
        )

        return canvas
