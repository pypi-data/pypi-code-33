import math

import numpy as np
import pytest

from pystork.activations import Sigmoid, Tanh, Relu


def test_sigmoid_value():

    x = np.array([0, 1, -1, 2])
    assert np.all(
        Sigmoid().get_value(x)
        == np.array([0.5, 1 / (1 + math.exp(-1)), 1 / (1 + math.exp(1)), 1 / (1 + math.exp(-2))])
    )


def test_sigmoid_derivative():

    x = np.array([[5.2]])

    # We will use approximative derivatives to check the derivatives
    eps = math.pow(10, -7)

    approximated_derivative = Sigmoid().get_approximate_derivative(x)
    derivative = Sigmoid().get_derivative(x)

    assert np.all(approximated_derivative - eps <= derivative) and np.all(
        derivative <= approximated_derivative + eps
    )


def test_sigmoid_derivative_when_value_present():

    x = np.array([[5.2]])

    # We will use approximative derivatives to check the derivatives
    eps = math.pow(10, -7)
    value_at_x = Sigmoid().get_value(x)
    approximated_derivative = Sigmoid().get_approximate_derivative(x)
    derivative = Sigmoid().get_derivative(x, value_at_x)

    assert np.all(approximated_derivative - eps <= derivative) and np.all(
        derivative <= approximated_derivative + eps
    )


def test_tanh_value():

    x = np.array([0, 1, -1, 2])
    assert (
        np.max(
            np.abs(
                Tanh().get_value(x)
                - np.array(
                    [
                        0,
                        (math.exp(1) - math.exp(-1)) / (math.exp(1) + math.exp(-1)),
                        (math.exp(-1) - math.exp(1)) / (math.exp(-1) + math.exp(1)),
                        (math.exp(2) - math.exp(-2)) / (math.exp(2) + math.exp(-2)),
                    ]
                )
            )
        )
        < 0.001
    )


def test_tanh_derivative():

    x = np.array([[7.2]])
    eps = math.pow(10, -7)

    approximate_derivative = Tanh().get_approximate_derivative(x, eps)
    derivative = Tanh().get_derivative(x)

    assert np.all(approximate_derivative - eps <= derivative) and np.all(
        derivative <= approximate_derivative + eps
    )


def test_tanh_derivative_with_value():

    x = np.array([[7.2]])
    eps = math.pow(10, -7)
    value_at_x = Tanh().get_value(x)
    approximate_derivative = Tanh().get_approximate_derivative(x, eps)
    derivative = Tanh().get_derivative(x, value_at_x)

    assert np.all(approximate_derivative - eps <= derivative) and np.all(
        derivative <= approximate_derivative + eps
    )


def test_relu_value():

    x = np.array([[5], [-2], [1], [-4], [0]])
    relu = Relu()
    value = relu.get_value(x)
    assert np.all(value == np.array([[5], [0], [1], [0], [0]]))


def test_relu_derivative():

    x = np.array([[5], [-2], [1], [-4], [0]])
    relu = Relu()
    derivative = relu.get_derivative(x)
    expected_derivative = np.array([[1], [0], [1], [0], [1]])
    assert np.all(derivative == expected_derivative)


def test_relu_approximative_derivative():

    x = np.array([[5], [-2], [1], [-4], [0]])
    with pytest.raises(Exception):
        Relu().get_approximate_derivative(x)
