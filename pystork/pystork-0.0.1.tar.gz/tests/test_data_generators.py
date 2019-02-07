from pystork.data_generators import threshold_data


def test_threshold_data():

    X, Y = threshold_data.generate_data(100, 0.2)

    assert X.shape == (1, 100)
    assert Y.shape == (1, 100)
    for i in range(100):
        if X[0, i] >= 0.2:
            assert Y[0, i] == 1
        else:
            assert Y[0, i] == 0
