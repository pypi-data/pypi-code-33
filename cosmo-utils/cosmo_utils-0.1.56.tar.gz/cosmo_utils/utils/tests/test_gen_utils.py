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
"""
Set of test functions for the `gen_utils` functions
"""

## Import modules

import numpy as np

import pytest

from cosmo_utils.utils import gen_utils
from cosmo_utils.custom_exceptions import LSSUtils_Error

# Functions

# Test function for `reshape_arr_1d` - Input type
arr_type_arr = ['11', '1+2', 2.0, np.nan]
@pytest.mark.parametrize('arr', arr_type_arr)
def test_reshape_arr_1d_type(arr):
    """
    Tests the function `cosmo_utils.utils.gen_utils.reshape_arr_1d`
    for input types.

    Parameters
    -----------
    arr : `numpy.ndarray` or array-like
        Array to be converted into 1-dimensional array.
    """
    ## Testing input types
    with pytest.raises(TypeError):
        gen_utils.reshape_arr_1d(arr)

# Test function for `reshape_arr_1d` - Dimensions
arr_dim_arr = [(1, 2, 3), (4, 5, 6, 7), (10, 4, 5, 10, 7)]
@pytest.mark.parametrize('arr_shape', arr_dim_arr)
def test_reshape_arr_1d_ndim(arr_shape):
    """
    Tests the function `cosmo_utils.utils.gen_utils.reshape_arr_1d`
    for input types.

    Parameters
    -----------
    arr : `numpy.ndarray` or array-like
        Array to be converted into 1-dimensional array.
    """
    arr = np.random.random(arr_shape)
    ## Testing input types
    with pytest.raises(LSSUtils_Error):
        gen_utils.reshape_arr_1d(arr)

# Test function for `reshape_arr_1d` - Shape
arr_shape_arr = [(10, (10,)), (5, (5,)), ((10, 5), (10, 5)),
                ((20, 20), (20, 20)), (5, (5,)), ((3, 3), (3, 3))]
@pytest.mark.parametrize('arr_shape, expected_shape', arr_shape_arr)
def test_reshape_arr_1d_shape(arr_shape, expected_shape):
    """
    Tests the function `cosmo_utils.utils.gen_utils.reshape_arr_1d`
    for input types.

    Parameters
    -----------
    arr_shape : `tuple` or `int`
        Shape of the array to create.

    expected_shape : `int` or `tuple`
        Expected shape for the array
    """
    # Creating array
    arr = np.random.random(arr_shape)
    # Checking result with function
    arr_out = gen_utils.reshape_arr_1d(arr)
    # Checking shape
    assert(arr_out.shape == expected_shape)
