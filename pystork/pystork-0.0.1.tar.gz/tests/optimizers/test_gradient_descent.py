# In order to test gradient descent, we will check build a very simple test of data, a model, execute gradient descent
# and make sure that it is converging and giving good results


import numpy as np

from pystork.activations import Tanh, Sigmoid
from pystork.costs.binary_classfication import BinaryClassificationCost
from pystork.data_generators import threshold_data
from pystork.initializers import RandomInitializer
from pystork.model import Layer, Model
from pystork.optimizers.gradient_descent import (
    GradientDescent,
    MiniBatchGradientDescent,
    Adam
)


def test_get_minibatches():

    X, Y = threshold_data.generate_data(samples_number=1000, threshold=0.2)

    mini_batch = MiniBatchGradientDescent(
        iterations_number=6000, learning_rate=0.1, mini_batch_size=64, print_cost=True
    )
    # pylint: disable=protected-access
    mini_batches = mini_batch._get_minibatches(X, Y)

    assert len(mini_batches) == 16
    for i in range(15):
        assert mini_batches[i][0].shape[1] == 64
        assert mini_batches[i][1].shape[1] == 64

    assert mini_batches[15][0].shape[1] == 40
    assert mini_batches[15][1].shape[1] == 40


def test_gradient_descent():

    X, Y = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    # We will build a model of 2 layers with 1 tanh and 1 sigmoid
    layer_1 = Layer(units_number=3, inputs_number=1, activation_function=Tanh())
    layer_2 = Layer(units_number=1, inputs_number=3, activation_function=Sigmoid())

    model = Model(
        layers=[layer_1, layer_2],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    gradient_descent = GradientDescent(
        iterations_number=15000, learning_rate=0.1, print_cost=True
    )
    costs = gradient_descent.optimize_cost(model, X, Y)
    assert costs[-1] <= 1

    X_test, Y_test = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    Y_pred = model.predict(X_test) >= 0.5
    precision = np.sum(np.abs(Y_pred == Y_test))/1000
    assert precision > 0.95


def test_mini_batch_gradient_descent():

    X, Y = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    # We will build a model of 4 layers with 3 relus and 1 sigmoid
    layer_1 = Layer(units_number=3, inputs_number=1, activation_function=Tanh())
    layer_2 = Layer(units_number=1, inputs_number=3, activation_function=Sigmoid())

    model = Model(
        layers=[layer_1, layer_2],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    mini_batch = MiniBatchGradientDescent(
        iterations_number=9000, learning_rate=0.1, mini_batch_size=200, print_cost=True
    )
    costs = mini_batch.optimize_cost(model, X, Y)
    assert costs[-1] <= 1

    X_test, Y_test = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    Y_pred = model.predict(X_test) >= 0.5

    precision = np.sum(np.abs(Y_pred == Y_test)) / 1000
    assert precision > 0.95


def test_gradient_descent_adam():

    X, Y = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    # We will build a model of 2 layers with 1 tanh and 1 sigmoid
    layer_1 = Layer(units_number=3, inputs_number=1, activation_function=Tanh())
    layer_2 = Layer(units_number=1, inputs_number=3, activation_function=Sigmoid())

    model = Model(
        layers=[layer_1, layer_2],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    gradient_descent = Adam(
        iterations_number=15000, learning_rate=0.1,
        mini_batch_size=1000,
        gradient_moment=0.,
        square_gradient_moment=0.,
        print_cost=True
    )
    costs = gradient_descent.optimize_cost(model, X, Y)
    assert costs[-1] <= 1

    X_test, Y_test = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    Y_pred = model.predict(X_test) >= 0.5
    precision = np.sum(np.abs(Y_pred == Y_test))/1000
    assert precision > 0.95


def test_mini_batch_gradient_descent_adam():

    X, Y = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    # We will build a model of 4 layers with 3 relus and 1 sigmoid
    layer_1 = Layer(units_number=3, inputs_number=1, activation_function=Tanh())
    layer_2 = Layer(units_number=1, inputs_number=3, activation_function=Sigmoid())

    model = Model(
        layers=[layer_1, layer_2],
        cost_function=BinaryClassificationCost(),
        initializer=RandomInitializer(),
    )

    mini_batch = Adam(
        iterations_number=9000,
        learning_rate=0.1,
        mini_batch_size=200,
        print_cost=True,
        gradient_moment=0,
        square_gradient_moment=0
    )
    costs = mini_batch.optimize_cost(model, X, Y)
    assert costs[-1] <= 1

    X_test, Y_test = threshold_data.generate_data(samples_number=1000, threshold=0.2)
    Y_pred = model.predict(X_test) >= 0.5

    precision = np.sum(np.abs(Y_pred == Y_test)) / 1000
    assert precision > 0.95
