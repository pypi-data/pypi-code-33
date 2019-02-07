import numpy as np

from pystork import helpers


# pylint: disable=unused-argument
def test_data_shuffle(mock_permutations):

    X = np.array([[1, 2, 3], [10, 20, 30]])
    Y = np.array([[-1, -2, -3]])

    shuffled_X, shuffled_Y = helpers.shuffle_data(X, Y)

    assert np.all(shuffled_X == np.array([[2, 1, 3], [20, 10, 30]]))
    assert np.all(shuffled_Y == np.array([[-2, -1, -3]]))
