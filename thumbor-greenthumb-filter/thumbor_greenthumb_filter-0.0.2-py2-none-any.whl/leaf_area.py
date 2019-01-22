#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from PIL import Image
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method(
        BaseFilter.PositiveNumber,#h_min
        BaseFilter.PositiveNumber,#s_min
        BaseFilter.PositiveNumber,#v_min
        BaseFilter.PositiveNumber,#h_max
        BaseFilter.PositiveNumber,#s_max
        BaseFilter.PositiveNumber,#v_max
    )
    def leaf_area(self, h_min=0, s_min=0, v_min=0, h_max=255, s_max=255, v_max=255):
        leaf_lower = (h_min, s_min, v_min)
        leaf_upper = (h_max, s_max, v_max)

        image =  np.array(self.engine.image)
        print(leaf_lower)
        blurred = cv2.GaussianBlur(image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, leaf_lower, leaf_upper)

        masked_output = cv2.bitwise_and(image, image, mask = mask)
        self.engine.image = Image.fromarray(masked_output)

    @filter_method(
        BaseFilter.PositiveNumber,#h_min
        BaseFilter.PositiveNumber,#s_min
        BaseFilter.PositiveNumber,#v_min
        BaseFilter.PositiveNumber,#h_max
        BaseFilter.PositiveNumber,#s_max
        BaseFilter.PositiveNumber,#v_max
    )
    def bud_area(self, h_min=0, s_min=0, v_min=0, h_max=255, s_max=255, v_max=255):
        leaf_lower = (h_min, s_min, v_min)
        leaf_upper = (h_max, s_max, v_max)

        image = self.engine.image.convert('RGB')
        image_data = np.array(pil_image)
        # Convert RGB to BGR
        image_data_bgr = open_cv_image[:, :, ::-1].copy()

        mask = detection_mask(leaf_lower, leaf_upper)

        mask = cv2.threshold(mask, 150, 255, cv2.THRESH_BINARY)[1]

        mask = cv2.erode(mask, None, iterations=4)
        mask = cv2.dilate(mask, None, iterations=2)

        masked_output = cv2.bitwise_and(image_data, image_data, mask = mask)
        self.engine.image = Image.fromarray(masked_output)

    def detection_mask(self, image_data, leaf_lower=(0, 0, 0), leaf_upper=(255, 255, 255)):
        blurred = cv2.GaussianBlur(image_data, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, leaf_lower, leaf_upper)
