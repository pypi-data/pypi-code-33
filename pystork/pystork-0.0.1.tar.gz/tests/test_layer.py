import numpy as np

from pystork.layer import Layer


def test_get_preactivation_with_save():

    layer = Layer(units_number=2, inputs_number=3, activation_function=None)
    layer.set_parameters(np.array([[1, 2, 3], [4, 5, 6]]), np.array([[1], [2]]))
    preactivation = layer.compute_preactivation(np.array([[0.5], [1], [2]]), save=True)

    expected_preactivation = np.array([[9.5], [21]])
    assert np.all(expected_preactivation == preactivation)
    assert np.all(expected_preactivation == layer.cache.preactivation)


def test_get_preactivation_without_save():

    layer = Layer(units_number=2, inputs_number=3, activation_function=None)
    layer.set_parameters(np.array([[1, 2, 3], [4, 5, 6]]), np.array([[1], [2]]))
    preactivation = layer.compute_preactivation(np.array([[0.5], [1], [2]]), save=False)

    expected_preactivation = np.array([[9.5], [21]])
    assert np.all(expected_preactivation == preactivation)
    assert layer.cache.preactivation is None


def test_execute_forward_propagation_with_save(layer):

    x = np.array([[-1], [1]])
    activation = layer.execute_forward_propagation(x, save=True)

    expected_activation = np.array([[0], [1]])
    assert np.all(activation == expected_activation)
    assert np.all(layer.cache.activation == expected_activation)
    assert np.all(layer.cache.forward_vector == x)


def test_execute_forward_propagation_without_save(layer):

    x = np.array([[-1], [1]])
    activation = layer.execute_forward_propagation(x, save=False)

    expected_activation = np.array([[0], [1]])
    assert np.all(activation == expected_activation)
    assert layer.cache.activation is None
    assert layer.cache.forward_vector is None


def test_execute_last_unit_backward_propagation(layer):

    x = np.array([[-1, 1], [1, -2]])
    layer.execute_forward_propagation(x, save=True)

    d_current_layer_preactivation = np.array([[1, 2], [2, -3]])
    d_preactivation = layer.execute_last_unit_backward_propagation(
        d_current_layer_preactivation
    )

    expected_d_preactivation = d_current_layer_preactivation
    expected_d_W = np.array([[0.5, -1.5], [-2.5, 4]])
    expected_d_bias = np.array([[1.5], [-0.5]])

    assert np.all(expected_d_preactivation == d_preactivation)
    assert np.all(layer.cache.d_W == expected_d_W)
    assert np.all(layer.cache.d_b == expected_d_bias)


def test_execute_hidden_backward_propagation(layer):

    x = np.array([[-1], [1]])
    layer.execute_forward_propagation(x, save=True)

    # we suppose that the next layer has 3 units
    next_layer_d_preactivation = np.array([[1], [2], [4]])
    next_layer_weights = np.array([[3, 4], [-2, 1], [-3, 2]])
    d_preactivation = layer.execute_backward_propagation(
        next_layer_d_preactivation=next_layer_d_preactivation,
        next_layer_weights=next_layer_weights,
    )

    expected_d_preactivation = np.array([[0], [14]])
    expected_d_W = np.array([[0., 0], [-14, 14]])
    expected_d_bias = np.array([[0], [14]])

    assert np.all(d_preactivation == expected_d_preactivation)
    assert np.all(layer.cache.d_W == expected_d_W)
    assert np.all(layer.cache.d_b == expected_d_bias)
