import numpy as np


def test_forward_propagation(forward_propagation_model, forward_training_data):
    forward_propagation_model.execute_forward_propagation(
        forward_training_data[0], forward_training_data[1]
    )
    assert (
        np.max(
            np.abs(
                forward_propagation_model.layers[0].cache.preactivation
                - np.array(
                    [
                        [1.738, 1.746, 1.748],
                        [-0.813, -0.733, -0.78767559],
                        [0.298, 0.322, 0.347],
                        [-0.227, -0.263, -0.223],
                    ]
                )
            )
        )
        < 0.01
    )

    assert (
        np.max(
            np.abs(
                forward_propagation_model.layers[0].cache.activation
                - np.array(
                    [
                        [0.94, 0.941, 0.941],
                        [-0.671, -0.625, -0.657],
                        [0.29, 0.311, 0.334],
                        [-0.223, -0.257, -0.219],
                    ]
                )
            )
        )
        < 0.01
    )

    assert (
        np.max(
            np.abs(
                forward_propagation_model.layers[1].cache.preactivation
                - np.array([[-1.30737426, -1.30844761, -1.30717618]])
            )
        )
        < 0.01
    )

    assert (
        np.max(
            np.abs(
                forward_propagation_model.layers[1].cache.activation
                - np.array([[0.21292656, 0.21274673, 0.21295976]])
            )
        )
        < 0.01
    )


def test_backward_propagation(backward_propagation_model, backward_training_data):

    # We execute the forward propagation before
    backward_propagation_model.execute_forward_propagation(
        backward_training_data[0], backward_training_data[1]
    )
    backward_propagation_model.execute_backward_propagation(backward_training_data[1])
    assert (
        np.max(
            np.abs(
                backward_propagation_model.layers[0].cache.d_W
                - np.array(
                    [
                        [0.003, -0.007],
                        [0.002, -0.006],
                        [-0.001, 0.003],
                        [-0.006, 0.0163],
                    ]
                )
            )
        )
        < 0.01
    )
    assert (
        0
        < np.abs(
            np.max(
                backward_propagation_model.layers[0].cache.d_b
                - np.array([[0.00176201], [0.00150995], [-0.00091736], [-0.00381422]])
            )
        )
        < 0.01
    )

    assert (
        np.max(
            np.abs(
                backward_propagation_model.layers[-1].cache.d_W
                - np.array([[0.00078841, 0.01765429, -0.00084166, -0.01022527]])
            )
        )
        < 0.01
    )
    assert (
        np.max(
            np.abs(
                backward_propagation_model.layers[-1].cache.d_b - np.array([[-0.16655712]])
            )
        )
        < 0.01
    )
