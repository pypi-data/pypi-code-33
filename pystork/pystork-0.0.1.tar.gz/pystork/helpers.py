from typing import Tuple
import numpy as np


def shuffle_data(
    training_inputs: np.array, training_labels: np.array
) -> Tuple[np.array, np.array]:
    """
    :param training_inputs:
    :param training_labels:
    :return: shuffled data (shuffled_training_inputs, shuffled_training_labels)
    """

    assert training_inputs.shape[1] == training_labels.shape[1]

    permutation = list(np.random.permutation(training_inputs.shape[1]))
    shuffled_training_inputs = training_inputs[:, permutation]
    shuffled_training_labels = training_labels[:, permutation]
    return shuffled_training_inputs, shuffled_training_labels
