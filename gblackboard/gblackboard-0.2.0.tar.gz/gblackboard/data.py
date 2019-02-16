# -*- coding: utf-8 -*-

import pickle

from .exception import UnsupportedDataType


def reconstruct(value):
    try:
        value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError as pe:
        raise UnsupportedDataType(
            "Cannot serialize given data: {}. Details: {}".format(value, pe))
    return value


def load(data):
    try:
        value = pickle.loads(data)
    except pickle.UnpicklingError as upe:
        raise UnsupportedDataType(
            "Cannot deserialize given data: {}. Details: {}".format(data, upe))
    return value
