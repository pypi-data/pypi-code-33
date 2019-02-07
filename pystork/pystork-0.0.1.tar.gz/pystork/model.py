"""
This file represents a model of a neural network
"""

from typing import List, Tuple

import numpy as np

from pystork.layer import Layer
from pystork.costs.abstract_cost import AbstractCostFunction
from pystork.initializers import AbstractInitializer


class Model:
    def __init__(
        self,
        layers: List[Layer],
        cost_function: AbstractCostFunction,
        initializer: AbstractInitializer,
    ):
        """
        :param layers: The list of ordered layers
        :param cost_function: The cost that we want to optimize
        :param normalize: A boolean indicating whether we want to normalize the inputs or not
        """

        self.layers = layers
        self.layers_number = len(layers)
        self.normalization_vector = np.ones((layers[0].inputs_number, 1))

        # We finally check the dimensions compatibility so that we lake sure that our vector products
        # will work correctly.
        self._check_dimensions_compatibility()

        self.cost = cost_function
        self.last_cost_computation = float("inf")
        self.initializer = initializer
        self.forward_propagation_result = None

    def normalize_inputs(self, training_inputs: np.array) -> np.array:
        """
        We normalize training inputs in the model, so that we use the normalization vector when predicting
        :param training_inputs:
        :return: normalized training inputs
        """
        self.normalization_vector = np.linalg.norm(
            training_inputs, axis=1, keepdims=True
        )

        return training_inputs / self.normalization_vector

    def _check_dimensions_compatibility(self):
        """
        checks the dimensions compatibility
        It raises an error if there is some dimension incompatibility
        """

        # We check the connections between layers
        if len(self.layers) > 1:
            for i in range(len(self.layers) - 1):
                assert self.layers[i].units_number == self.layers[i + 1].inputs_number

    def initialize_layers(self):
        for layer in self.layers:
            layer.initialize(self.initializer)

    def execute_forward_propagation(
        self, training_inputs: np.array, training_labels: np.array
    ) -> Tuple[np.array, float]:
        """
        executes the forward propagation and returns the predictions and the cost
        """

        for layer_number in range(self.layers_number):
            if layer_number > 0:
                training_inputs = self.layers[layer_number - 1].cache.activation

            current_layer = self.layers[layer_number]
            current_layer.execute_forward_propagation(training_inputs, save=True)
        self.last_cost_computation = self.cost.compute(
            y_pred=self.layers[-1].cache.activation, y_labels=training_labels
        )
        return self.forward_propagation_result, self.last_cost_computation

    def execute_backward_propagation(self, training_labels: np.array):

        # We have to forward propagate before backward propagation
        assert self.layers[-1].cache.activation is not None

        cost_function_derivative = self.cost.compute_preactivation_derivative(
            self.layers[-1].cache.activation, training_labels
        )

        # For the last layer, we give it this derivative as the result of its current preactivation derivative
        last_layer = self.layers[-1]
        last_layer.execute_last_unit_backward_propagation(
            current_layer_d_preactivation=cost_function_derivative
        )

        if self.layers_number > 1:
            for i in reversed(range(self.layers_number - 1)):
                next_layer_d_preactivation = self.layers[i + 1].cache.d_preactivation
                next_layer_weights = self.layers[i + 1].W
                self.layers[i].execute_backward_propagation(
                    next_layer_d_preactivation, next_layer_weights
                )

    def predict(self, x: np.array) -> np.array:

        assert x.shape[0] == self.layers[0].inputs_number

        x = x / self.normalization_vector
        for layer in self.layers:
            x = layer.execute_forward_propagation(x, save=False)
        return x
