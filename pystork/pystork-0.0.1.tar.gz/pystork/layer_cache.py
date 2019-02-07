"""
This file implements the class that represents the cache of a layer during forward and backward
propagations
"""
from typing import Union
import numpy as np


class LayerCache:
    def __init__(self, units_number: int, inputs_number: int):

        self.preactivation: np.array = None
        self.activation: np.array = None

        # d_preactivation is the derivative of the cost function on the preactivation vector
        self.d_preactivation: np.array = None
        # d_W and d_b are the derivatives of the cost function on W and b respectively
        self.d_W: Union[np.array, float] = None
        self.d_b: Union[np.array, float] = None

        # forward_vector is the vector on which we have computed the forward propagation
        self.forward_vector = None

        self.d_W_momentum = np.zeros((units_number, inputs_number))
        self.d_b_momentum = np.zeros((units_number, 1))

        self.d_W_square_momentum = np.zeros((units_number, inputs_number))
        self.d_b_square_momentum = np.zeros((units_number, 1))
