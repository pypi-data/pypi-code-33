"""Contains the base Layer class, from which all layers inherit.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


class Rmsprop:
    @staticmethod
    def update_parameters(layer, keys, learning_rate, decay=0.9):
        epsilon = 1e-8
        temp = {}
        for key in keys:
            temp["S_d" + key] = np.zeros(layer[key].shape)

        for key in keys:
            temp["S_d" + key] = decay * temp["S_d" + key] + (1 - decay) * layer["d" + key] ** 2
            layer[key] -= (learning_rate / (np.sqrt(temp["S_d" + key] + epsilon))) * layer["d" + key]
        return layer
