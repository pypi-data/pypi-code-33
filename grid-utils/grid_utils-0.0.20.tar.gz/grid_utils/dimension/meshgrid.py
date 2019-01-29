# -*- coding:utf-8 -*-

import numpy as np

__all__ = ['smart_meshgrid']

def smart_meshgrid(*xi):
    if not xi:
        return

    ndims = np.array([np.ndim(x) for x in xi])
    if np.all(ndims == 1):
        return np.meshgrid(*xi)
    elif np.all(ndims == len(ndims)):
        shapes = np.array([np.shape(x) for x in xi])
        if np.all(shapes == shapes[0]):
            return xi
        else:
            raise ValueError("Bad shapes for smart_meshgrid.")
    else:
        raise ValueError("Bad ndims for smart_meshgrid: {}".format(ndims))
