"""
This file represents the interface for an optimizer
"""

from abc import ABC, abstractmethod
import numpy as np
from pystork.model import Model


class AbstractOptimizer(ABC):
    @abstractmethod
    def optimize_cost(
        self, model: Model, training_inputs: np.array, training_labels: np.array
    ):
        """
        :param model:
        :param training_input
        :param training_labels
        :return: optimize the cost of the specified model: it trains the model
        """

    @staticmethod
    def check_dimensions(
        model: Model, training_inputs: np.array, training_labels: np.array
    ):
        """
        :param model:
        :param training_inputs:
        :param training_labels:
        :return: check the dimensions cohesion between model, features and labels
        """
        assert training_inputs.shape[1] == training_labels.shape[1]
        assert training_labels.shape[0] == model.layers[-1].units_number
