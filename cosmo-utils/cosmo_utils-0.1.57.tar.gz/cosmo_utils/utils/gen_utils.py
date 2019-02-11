#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-31
# Last Modified: 2018-05-31
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "reshape_arr_1d",
                    "array_insert"]
"""
General tools for a day-to-day use.
"""

# Import modules

import numpy as np

from cosmo_utils.utils import file_utils as fd
from cosmo_utils.custom_exceptions import LSSUtils_Error

# Functions

def reshape_arr_1d(arr):
    """
    Transforms the array intoa 1-dimensional array, if necessary.

    Parameters
    -----------
    arr : `numpy.ndarray` or array-like
        Array to be converted into 1-dimensional array.

    Returns
    -----------
    arr_new : `numpy.ndarray` or array-like
        Converted array into 1-dimensional array if needed.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking input parameters
    arr_valid_types = (list, np.ndarray)
    # `arr`
    if not (isinstance(arr, arr_valid_types)):
        msg = '{0} `arr` ({1}) is not a valid input type!'.format(file_msg,
            type(arr))
        raise TypeError(msg)
    # Dimensions
    if (isinstance(arr, arr_valid_types)):
        if not (np.asarray(arr).ndim in [1, 2]):
            msg = '{0} The shape of `arr` ({1}) can only have 1 or 2 '
            msg += 'dimensions'
            msg = msg.format(file_msg, np.asarray(arr).ndim)
            raise LSSUtils_Error(msg)
    # Converting to Numpy array
    arr = np.asarray(arr)
    # Trying to reshape it
    if (arr.ndim == 2):
        if (arr.shape[1] == 1):
            arr = arr.reshape(len(arr),)

    return arr

def array_insert(arr1, arr2, axis=1):
    """
    Joins the two arrays into a `single` multi-dimensional array.

    Parameters
    ------------
    arr1 : `numpy.ndarray`
        1st array to merge

    arr2 : `numpy.ndarray`
        2nd array to merge

    axis : `axis object`
        Axis to use for the merging

    Returns
    ----------
    arr_merged : `numpy.ndarray`
        Merged array from `arr1` and `arr2`.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking input parameters
    arr_valid_types = (list, np.ndarray)
    # `arr1`
    if not (isinstance(arr1, arr_valid_types)):
        '{0} `arr1` ({1}) is not array-like!'.format(file_msg, type(arr1))
        raise ValueError(msg)
    # `arr2`
    if not (isinstance(arr2, arr_valid_types)):
        '{0} `arr2` ({1}) is not array-like!'.format(file_msg, type(arr2))
        raise ValueError(msg)
    #
    # Merging arrays
    arr_merged = np.insert(arr1, len(arr1.T), arr2, axis=axis)

    return arr3
