"""
Configuration and fixtures for pytest.
https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions
"""

from typing import Tuple
from unittest.mock import MagicMock

# pylint: disable=redefined-outer-name
import numpy as np
import pytest

from pystork.activations import Relu, Tanh, Sigmoid
from pystork.costs.binary_classfication import BinaryClassificationCost
from pystork.initializers import RandomInitializer
from pystork.layer import Layer
from pystork.model import Model


@pytest.fixture
def layer() -> Layer:
    """
    :return: a simple relu layer with configured parameters
    """
    layer = Layer(units_number=2, inputs_number=2, activation_function=Relu())
    layer.set_parameters(np.array([[1, 0], [0, 1]]), np.array([[0], [0]]))
    return layer


@pytest.fixture
def forward_propagation_model() -> Model:
    """
    a simple model with one hidden layer used for forward propagation
    """

    hidden_layer = Layer(units_number=4, inputs_number=2, activation_function=Tanh())
    output_layer = Layer(units_number=1, inputs_number=4, activation_function=Sigmoid())

    model = Model(
        layers=[hidden_layer, output_layer],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    hidden_layer.W = np.array(
        [
            [-0.00416758, -0.00056267],
            [-0.02136196, 0.01640271],
            [-0.01793436, -0.00841747],
            [0.00502881, -0.01245288],
        ]
    )
    hidden_layer.b = np.array([[1.74481176], [-0.7612069], [0.3190391], [-0.24937038]])
    output_layer.W = np.array([-0.01057952, -0.00909008, 0.00551454, 0.02292208])
    output_layer.b = np.array([[-1.3]])

    return model


@pytest.fixture
def forward_training_data() -> Tuple[np.array, np.array]:
    """
    :return: (training_inputs, training_labels)
    """
    training_inputs = np.array(
        [[1.62434536, -0.61175641, -0.52817175], [-1.07296862, 0.86540763, -2.3015387]]
    )

    training_labels = np.array([[True, False, False]])

    return training_inputs, training_labels


@pytest.fixture
def backward_propagation_model() -> Model:
    """
    a simple model with one hidden layer used for forward propagation
    """

    hidden_layer = Layer(units_number=4, inputs_number=2, activation_function=Tanh())
    output_layer = Layer(units_number=1, inputs_number=4, activation_function=Sigmoid())
    model = Model(
        layers=[hidden_layer, output_layer],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    hidden_layer.W = np.array(
        [
            [-0.00416758, -0.00056267],
            [-0.02136196, 0.01640271],
            [-0.01793436, -0.00841747],
            [0.00502881, -0.01245288],
        ]
    )
    hidden_layer.b = np.array([[.0], [.0], [.0], [.0]])
    output_layer.W = np.array([[-0.01057952, -0.00909008, 0.00551454, 0.02292208]])
    output_layer.b = np.array([[0]])

    return model


@pytest.fixture
def backward_training_data() -> Tuple[np.array, np.array]:
    """
    :return: (training_inputs, training_lables)
    """
    training_inputs = np.array(
        [[1.62434536, -0.61175641, -0.52817175], [-1.07296862, 0.86540763, -2.3015387]]
    )

    training_labels = np.array([[True, False, True]])

    return training_inputs, training_labels


@pytest.fixture
def mock_permutations(mocker) -> MagicMock:

    return mocker.patch("numpy.random.permutation", return_value=[1, 0, 2])
