"""
This file represents the cost function for binary classification
"""
import math

import numpy as np

from pystork.costs.abstract_cost import AbstractCostFunction


class BinaryClassificationCost(AbstractCostFunction):
    def compute(self, y_pred: np.array, y_labels: np.array) -> float:

        # This function works only when y_pred and y_labels have the same dimension
        assert y_pred.shape == y_labels.shape
        # we need also to make sure that all values are between 0 and 1
        assert np.all(y_labels <= 1) and np.all(y_labels >= 0)
        assert np.all(y_pred <= 1) and np.all(y_pred >= 0)
        # in order to avoid nan values when using log, we make y_pred strictly lower than
        #  0 and bigger than 1
        epsilon = math.pow(10, -5)
        y_pred = np.maximum(np.minimum(y_pred, 1 - epsilon), epsilon)
        labels_number = y_labels.shape[1]
        cost = -(1 / labels_number) * np.sum(
            np.multiply(y_labels, np.log(y_pred))
            + np.multiply(1 - y_labels, np.log(1 - y_pred))
        )
        return np.squeeze(cost)

    def compute_preactivation_derivative(
        self, y_pred: np.array, y_labels: np.array
    ) -> np.array:
        """
        We assume that the last preactivation function is a sigmoid function
        """
        assert y_pred.shape == y_labels.shape

        return y_pred - y_labels
