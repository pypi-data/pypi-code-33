"""
This python file represents a layer in a neural network model
"""

from typing import Union
import numpy as np

from pystork.activations import AbstractActivation
from pystork.initializers import AbstractInitializer, ZerosInitializer
from pystork.layer_cache import LayerCache


class Layer:
    def __init__(
        self,
        units_number: int,
        inputs_number: int,
        activation_function: AbstractActivation,
    ):

        self.units_number = units_number
        self.inputs_number = inputs_number
        self.activation_function = activation_function
        # W to denote the weights
        self.W: Union[np.array, float] = None
        # b to denote the bias vector
        self.b: Union[np.array, float] = None

        self.cache = LayerCache(self.units_number, self.inputs_number)

    def compute_preactivation(self, x: np.array, save: bool) -> np.array:
        """
        :param x: The input vector
        :param save: A boolean indicating whether we store results or not
        :return: The preactivation
        """
        assert self.W is not None and self.b is not None
        assert self.inputs_number == x.shape[0]
        preactivation = np.dot(self.W, x) + self.b
        if save:
            self.cache.preactivation = preactivation
            # Assert dimensions
            assert self.cache.preactivation.shape == (self.units_number, x.shape[1])

        return preactivation

    def execute_forward_propagation(self, x: np.array, save: bool = True) -> np.array:
        """
        :param x: The input vector
        :param save: A boolean indicating whether we store results or not
        :return: The result of the layer: the activation
        """

        preactivation = self.compute_preactivation(x, save)

        activation = self.activation_function.get_value(preactivation)
        if save:
            self.cache.forward_vector = x
            self.cache.activation = activation

        # Assert dimensions
        assert activation.shape == (self.units_number, x.shape[1])
        return activation

    def execute_last_unit_backward_propagation(
        self, current_layer_d_preactivation: np.array
    ):
        """
        :param current_layer_d_preactivation: The derivative of the cost function on the preactivation vector of
        this layer
        :return: current_layer_d_preactivation
        """

        self.cache.d_preactivation = current_layer_d_preactivation
        self.get_parameters_derivatives()
        self.check_derivatives_dimensions()
        return self.cache.d_preactivation

    def execute_backward_propagation(
        self, next_layer_d_preactivation: np.array, next_layer_weights: np.array
    ):
        """
        :param next_layer_d_preactivation: The derivative of the cost function on the preactivation of the
        next layer. if it is not given, then we have to compute it
        :param next_layer_weights: The next layer weights
        :return: The derivative of the cost function on the preactivation vector of
        this layer
        """

        self.cache.d_preactivation = np.dot(
            next_layer_weights.T, next_layer_d_preactivation
        ) * self.activation_function.get_derivative(
            self.cache.preactivation, value_at_x=self.cache.activation
        )
        self.get_parameters_derivatives()

        self.check_derivatives_dimensions()
        return self.cache.d_preactivation

    def get_parameters_derivatives(self):

        labels_number = self.cache.forward_vector.shape[1]
        self.cache.d_W = (1 / labels_number) * np.dot(
            self.cache.d_preactivation, self.cache.forward_vector.T
        )
        self.cache.d_b = (1 / labels_number) * np.sum(
            self.cache.d_preactivation, axis=1, keepdims=True
        )

    def initialize(self, initializer: AbstractInitializer):
        if self.W is None:
            weights_initialization = initializer.get_values(
                x_dim=self.units_number, y_dim=self.inputs_number
            )
            self.W = weights_initialization
        # We always initialize the bias with zeros. But you can change this if you want :)
        if self.b is None:
            bias_initialization = ZerosInitializer().get_values(
                x_dim=self.units_number, y_dim=1
            )
            self.b = bias_initialization

        # We also set the cache of

    def set_parameters(self, new_W: np.array, new_b: np.array) -> None:

        self.W = new_W
        self.b = new_b

    def check_derivatives_dimensions(self):

        assert self.cache.d_preactivation.shape[0] == self.units_number
        assert self.cache.d_W.shape == (self.units_number, self.inputs_number)
        assert self.cache.d_b.shape == (self.units_number, 1)
