import numpy as np

def is_binary_message(message):
    message = np.array(message)
    _or_array = np.logical_or(message == 0, message == 1)
    return np.all(_or_array)
