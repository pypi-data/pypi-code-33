"""
This file represents an abstract activation function and many well-known activation functions
"""

from abc import ABC, abstractmethod
import math

import numpy as np


class AbstractActivation(ABC):
    @abstractmethod
    def get_value(self, x: np.array):
        """
        The value of the activation on the array (element wise operation)
        """

    @abstractmethod
    def get_derivative(self, x: np.array, value_at_x: np.array = None):
        """
        Get the derivative of the activation function on x (element wise operation)
        """

    def get_approximate_derivative(self, x: np.array, eps: float = math.pow(10, -7)):
        """
        :param x: the array on which we want to compute the approximate derivative (element wise)
        :param eps: the epsilon used for the approximation (we recommend to not change it)
        :return: the approximate derivative
        """
        return (self.get_value(x + eps) - self.get_value(x - eps)) / (2 * eps)


class Sigmoid(AbstractActivation):
    def get_value(self, x: np.array) -> np.array:

        return 1 / (1 + np.exp(-x))

    def get_derivative(self, x: np.array, value_at_x: np.array = None) -> np.array:

        # The derivative on x is equal to sigmoid(x) * (1 - sigmoid(x))
        if value_at_x is None:
            sigmoid_value = self.get_value(x)
        else:
            sigmoid_value = value_at_x

        return sigmoid_value * (1 - sigmoid_value)


class Relu(AbstractActivation):
    def get_value(self, x: np.array) -> np.array:

        return np.maximum(x, 0)

    def get_derivative(self, x: np.array, value_at_x: np.array = None) -> np.array:

        # The derivative of relu is 0 when value is less than 0 else 1
        # Mathematically speaking, there is no derivative on 0, but we will consider that it is
        # equal to 1

        return x >= 0

    def get_approximate_derivative(self, x: np.array, eps: float = math.pow(10, -7)):

        # We highly do not recommend to use the approxilate derivative when using a relu function
        raise Exception("Do not use derivative approximate on Relu")


class Tanh(AbstractActivation):
    def get_value(self, x: np.array) -> np.array:

        return np.tanh(x)

    def get_derivative(self, x: np.array, value_at_x: np.array = None) -> np.array:

        # The derivative on x is equal to 1 + tanh^2
        if value_at_x is None:
            tanh_value = self.get_value(x)
        else:
            tanh_value = value_at_x
        return 1 - np.power(tanh_value, 2)
