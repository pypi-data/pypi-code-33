#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-17
# Last Modified: 2018-05-17
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
"""
Set of test functions for the `ml_utils` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.ml import ml_utils as cml
from   cosmo_utils.custom_exceptions import LSSUtils_Error

# Functions

## Testing function `data_preprocessing` - Data type
feat_arr_shape_arr = [(10, 3), (20, 1), (10, 5)]
@pytest.mark.parametrize('n_samples, n_features', feat_arr_shape_arr)
def test_data_preprocessing(n_samples, n_features, pre_opt='no'):
    """
    Tests the function `~cosmo_utils.ml.ml_utils.data_preprocessing`
    for input and output parameters

    Parameters
    ------------
    n_samples : int
        Total number of samples. This variable is used to construct the
        array of features with shape [n_samples, n_features]

    n_features : int
        Total number of features. This variable is used to construct the
        array of features with shape [n_samples, n_features]

    pre_opt : {'min_max', 'standard', 'normalize', 'no'} `str`, optional
        Type of preprocessing to do on `feat_arr`.

        Options:
            - 'min_max' : Turns `feat_arr` to values between (0,1)
            - 'standard' : Uses `~sklearn.preprocessing.StandardScaler` method
            - 'normalize' : Uses the `~sklearn.preprocessing.Normalizer` method
            - 'no' : No preprocessing on `feat_arr`
    """
    ## Constructing `feat_arr`
    feat_arr = np.random.random_sample((n_samples, n_features))
    # Checking output
    feat_arr_out = cml.data_preprocessing(feat_arr, pre_opt=pre_opt)
    # Comparing arrays
    np.testing.assert_array_equal(feat_arr_out, feat_arr)

## Testing function `data_preprocessing` - Data type - `feat_arr`
feat_arr_shape_arr = ['test', None, 1, 'abc']
pre_opt_opt_arr    = ['min_max', 'standard', 'normalize', 'no']
@pytest.mark.parametrize('feat_arr', feat_arr_shape_arr)
@pytest.mark.parametrize('pre_opt' , pre_opt_opt_arr)
def test_data_processing_feat_arr_type(feat_arr, pre_opt):
    """
    Tests the function `~cosmo_utils.ml.ml_utils.data_preprocessing`
    for input and output parameters.
    This function tests for the input type of `feat_arr`

    Parameters
    -----------
    feat_arr : `numpy.ndarray`
        Array of feature values. This array is used for training a
        ML algorithm.

    pre_opt : {'min_max', 'standard', 'normalize', 'no'} `str`, optional
        Type of preprocessing to do on `feat_arr`.

        Options:
            - 'min_max' : Turns `feat_arr` to values between (0,1)
            - 'standard' : Uses `~sklearn.preprocessing.StandardScaler` method
            - 'normalize' : Uses the `~sklearn.preprocessing.Normalizer` method
            - 'no' : No preprocessing on `feat_arr`

    Raises
    ----------
    LSSUtils_Error : Exception
        This error gets raised when `ang` is not a digit or a number.
    """
    # Raising error
    with pytest.raises(LSSUtils_Error):
        cml.data_preprocessing(feat_arr, pre_opt)

## Testing function `data_preprocessing` - Data type - `pre_opt`
feat_arr_shape_arr = [np.array((10, 5))]
pre_opt_opt_arr    = ['min_max_2', 1, None, 'testing']
@pytest.mark.parametrize('feat_arr', feat_arr_shape_arr)
@pytest.mark.parametrize('pre_opt' , pre_opt_opt_arr)
def test_data_processing_pre_opt_type(feat_arr, pre_opt):
    """
    Tests the function `~cosmo_utils.ml.ml_utils.data_preprocessing`
    for input and output parameters.
    This function tests for the input type of `pre_opt`

    Parameters
    -----------
    feat_arr : `numpy.ndarray`
        Array of feature values. This array is used for training a
        ML algorithm.

    pre_opt : {'min_max', 'standard', 'normalize', 'no'} `str`, optional
        Type of preprocessing to do on `feat_arr`.

        Options:
            - 'min_max' : Turns `feat_arr` to values between (0,1)
            - 'standard' : Uses `~sklearn.preprocessing.StandardScaler` method
            - 'normalize' : Uses the `~sklearn.preprocessing.Normalizer` method
            - 'no' : No preprocessing on `feat_arr`

    Raises
    ----------
    LSSUtils_Error : Exception
        This error gets raised when `ang` is not a digit or a number.
    """
    # Raising error
    with pytest.raises(LSSUtils_Error):
        cml.data_preprocessing(feat_arr, pre_opt)
