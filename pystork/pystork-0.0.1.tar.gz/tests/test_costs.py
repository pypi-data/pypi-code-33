import math
import numpy as np

from pystork.activations import Sigmoid
from pystork.costs.binary_classfication import BinaryClassificationCost


def test_binary_classification_cost():

    labels = np.array([[1, 0, 1, 0]])

    binary_classification_cost = BinaryClassificationCost()

    eps = math.pow(10, -7)
    good_predictions = np.array([[1 - eps, eps, 1 - eps, eps]])
    bad_predictions = np.array([[eps, 1 - eps, eps, 1 - eps]])
    avg_prediction = np.array([[0.5, 0.5, 0.5, 0.5]])

    good_cost = binary_classification_cost.compute(good_predictions, labels)
    bad_cost = binary_classification_cost.compute(bad_predictions, labels)
    avg_cost = binary_classification_cost.compute(avg_prediction, labels)

    assert 0 < good_cost < math.pow(10, -4)
    assert bad_cost > 10
    assert 0.5 < avg_cost < 2


def test_binary_classification_derivative():

    labels = np.array([[1]])

    preactivation = np.array([[5]])
    y_pred = Sigmoid().get_value(preactivation)

    binary_classification_cost = BinaryClassificationCost()
    derivative = binary_classification_cost.compute_preactivation_derivative(
        y_pred, labels
    )

    eps = math.pow(10, -7)
    approximated_derivative = (
        binary_classification_cost.compute(
            Sigmoid().get_value(preactivation + eps), labels
        )
        - binary_classification_cost.compute(
            Sigmoid().get_value(preactivation - eps), labels
        )
    ) / (2 * eps)

    assert np.all(derivative <= approximated_derivative + eps)
    assert np.all(approximated_derivative - eps <= derivative)
