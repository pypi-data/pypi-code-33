import numpy as np
from pystork.initializers import RandomInitializer, ZerosInitializer


def test_zero_initializer():

    initializer = ZerosInitializer()
    assert np.all(initializer.get_values(3, 2) == np.array([[0, 0], [0, 0], [0, 0]]))


def test_random_initializer():
    initializer = RandomInitializer()
    assert initializer.get_values(x_dim=2, y_dim=3).shape == (2, 3)
