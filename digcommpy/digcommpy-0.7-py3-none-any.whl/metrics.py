import numpy as np
from sklearn.metrics import zero_one_loss

from .checks import is_binary_message

def ber(y_true, y_pred, normalize=True):
    """Calculate the Bit Error Ratio (BER) between two arrays.

    Parameters
    ----------
    y_true : numpy.array
        Array with the true bits. The shape is [num_messages, num_bits].
    y_pred : numpy.array
        Array with the predicted bits. Same shape as `y_true`.
    normalize : bool, optional
        If True, the results is normalized to be between 0 and 1. Otherwise,
        the number of errors is returned.

    Returns
    -------
    ber : float
        Bit error ratio or number of bit errors
    """
    if not (is_binary_message(y_true) and is_binary_message(y_pred)):
        raise ValueError("Only binary messages can be used to calculate the BER.")
    return zero_one_loss(np.ravel(y_true), np.ravel(y_pred), normalize=normalize)


def bler(y_true, y_pred, normalize=True):
    """Calculate the Block Error Ratio (BLER) between two arrays.

    Parameters
    ----------
    y_true : numpy.array
        Array with the true bits. The shape is [num_messages, num_bits].
    y_pred : numpy.array
        Array with the predicted bits. Same shape as `y_true`.
    normalize : bool, optional
        If True, the results is normalized to be between 0 and 1. Otherwise,
        the number of errors is returned.

    Returns
    -------
    bler : float
        Block error ratio
    """
    return zero_one_loss(y_true, y_pred, normalize=normalize)
