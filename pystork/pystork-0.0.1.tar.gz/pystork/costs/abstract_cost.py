"""
This file represents the interface for a cost function
"""

from abc import ABC, abstractmethod
import numpy as np


class AbstractCostFunction(ABC):
    @abstractmethod
    def compute(self, y_pred: np.array, y_labels: np.array) -> float:
        """
        :param y_pred:
        :param y_labels:
        :return: the cost with regard to predictions and true labels
        """

    @abstractmethod
    def compute_preactivation_derivative(
        self, y_pred: np.array, y_labels: np.array
    ) -> np.array:
        """
        :param y_pred:
        :param y_labels:
        :return: The derivative on the preactivate vector of the final layer
        :return: The derivative on the preactivate vector of the final layer
        :return: The derivative on the preactivate vector of the final layer
        :return: The derivative on the preactivate vector of the final layer
        :return: The derivative on the preactivate vector of the final layer
        :return: The derivative on the preactivate vector of the final layer
        """
