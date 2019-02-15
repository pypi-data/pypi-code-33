# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Functions to help with the construction of array
interfaces with reference to

https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.interface.html#__array_interface__
"""
import sys
from .exceptions import CodedValueError


data_types = {
    't': "Bit field",
    'b': "Boolean",
    'i': "Integer",
    'u': "Unsigned integer",
    'f': "Floating point",
    'c': "Complex floating point",
    'm': "Timedelta",
    'M': "Datetime",
    'O': "Object",
    'S': "String",
    'U': "Unicode",
    'V': "Other"
    }


def typestr(data_type='f', nbytes=8):
    """Construct the ``typestr`` value for the
    array interface.

    :param str data_type: Code that denotest the basic
        type of the array.
    :param int nbytes: Number of bytes the type uses.
    :raises ValueError: If the byteorder of the system
        is not supported.
    :raises ValueError: If the data-type is not
	supported.
    :rtype: str
    """
    if data_type not in data_types:
        raise CodedValueError(1000, "Data-type not supported")

    if sys.byteorder == 'little':
        typestr = '<' + data_type + str(nbytes)
    elif sys.byteorder == 'big':
        typestr = '>' + data_type + str(nbytes)
    else:
        raise CodedValueError(
            1001, "Unsupported byteorder: Neither little nor big-endian"
            )
    return typestr
