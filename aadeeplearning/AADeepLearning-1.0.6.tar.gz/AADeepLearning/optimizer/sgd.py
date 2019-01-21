"""Contains the base Layer class, from which all layers inherit.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


class Sgd:
    @staticmethod
    def update_parameters(layer, keys, learning_rate):
        for key in keys:
            layer[key] -= learning_rate * layer["d" + key]
        return layer
