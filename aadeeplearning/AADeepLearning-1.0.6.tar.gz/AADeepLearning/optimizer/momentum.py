"""Contains the base Layer class, from which all layers inherit.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


class Momentum():
    @staticmethod
    def update_parameters(layer, keys, learning_rate, momentum_coefficient):
        temp = {}
        for key in keys:
            temp["V_d"+key] = np.zeros(layer[key].shape)

        for key in keys:
            temp["V_d"+key] = momentum_coefficient*temp["V_d"+key]+layer["d"+key]
            layer[key] -= learning_rate*temp["V_d"+key]
        return layer
