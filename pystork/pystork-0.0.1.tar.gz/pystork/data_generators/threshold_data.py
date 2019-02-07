"""
the threshold data is a 1 * samples_number dimension data where the label of each point is 1 if the value is
greater than a specified threshold, otherwise 0
"""
from typing import Tuple
import numpy as np


def generate_data(
    samples_number: int, threshold: float = 0.
) -> Tuple[np.array, np.array]:
    """
    :return: data and its labels
    """

    X = np.random.randn(1, samples_number)
    Y = X >= threshold
    return X, Y
