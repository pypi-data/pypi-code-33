#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-17
# Last Modified: 2018-05-31
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = ["data_preprocessing",
                  "train_test_dataset",
                  "scoring_methods"]

# Importing modules
import scipy

import numpy as np
import pandas as pd

from cosmo_utils.utils import file_utils as fd
from cosmo_utils.utils import gen_utils as gu
from cosmo_utils.custom_exceptions import LSSUtils_Error

# ML modules
import sklearn.metrics          as skmetrics
import sklearn.model_selection  as skms
import sklearn.preprocessing    as skpre

# Extra modules

## Functions

# Data preprocessing
def data_preprocessing(feat_arr, pre_opt='min_max', reshape=False):
    """
    Preprocess the data used, in order to clean and make the data more
    suitable for the machine learning algorithms

    Parameters
    -----------
    feat_arr : `numpy.ndarray`, `list`, `pandas.DataFrame`
        Array of feature values. This array is used for training a
        ML algorithm.

    pre_opt : {'min_max', 'standard', 'normalize', 'no'} `str`, optional
        Type of preprocessing to do on `feat_arr`.

        Options:
            - 'min_max' : Turns `feat_arr` to values between (0,1)
            - 'standard' : Uses `~sklearn.preprocessing.StandardScaler` method
            - 'normalize' : Uses the `~sklearn.preprocessing.Normalizer` method
            - 'no' : No preprocessing on `feat_arr`

    reshape : `bool`, optional
        If True, it reshapes `feat_arr` into a 1d array if its shapes is
        equal to (ncols, 1), where `ncols` is the number of columns.
        This variable is set to `False` by default.

    Returns
    -----------
    feat_arr_scaled : `numpy.ndarray`
        Rescaled version of `feat_arr` based on the choice of `pre_opt`.

    Notes
    -----------
    For more information on how to pre-process your data, see
    `http://scikit-learn.org/stable/modules/preprocessing.html`_.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    # `feat_arr`
    feat_arr_type_valid = (list, np.ndarray, pd.DataFrame)
    if not (isinstance(feat_arr, feat_arr_type_valid)):
        msg = '{0} `feat_arr` ({1}) is not a valid input type'.format(
            file_msg, type(feat_arr))
        raise LSSUtils_Error(msg)
    # `pre_opt`
    pre_opt_valid = ['min_max', 'standard', 'normalize', 'no']
    if not (pre_opt in pre_opt_valid):
        msg = '{0} `pre_opt` ({1}) is not a valid input'.format(
            file_msg, pre_opt)
        raise LSSUtils_Error(msg)
    ##
    ## Reshaping `feat_arr`
    if reshape:
        feat_arr = gu.reshape_arr_1d(feat_arr)
    ##
    ## Scaling `feat_arr`
    if (pre_opt == 'min_max'):
        # Scaler
        scaler = skpre.MinMaxScaler(feature_range=(0, 1))
        # Rescaling
        feat_arr_scaled = scaler.fit_transform(feat_arr)
    ## Standardize Data
    if pre_opt == 'standard':
        # Scaler
        scaler = skpre.StandardScaler().fit(feat_arr)
        # Rescaling
        feat_arr_scaled = scaler.transform(feat_arr)
    ## Normalize Data
    if pre_opt == 'normalize':
        # Scaler
        scaler = skpre.Normalizer().fit(feat_arr)
        # Rescaling
        feat_arr_scaled = scaler.transform(feat_arr)
    ## No Preprocessing
    if pre_opt == 'no':
        feat_arr_scaled = feat_arr

    return feat_arr_scaled

# Train-Test Data Split
def train_test_dataset(pred_arr, feat_arr, pre_opt='min_max',
    shuffle_opt=True, random_state=0, test_size=0.25, reshape=False,
    return_idx=False):
    """
    Function to create the training and testing datasets for a given set
    of features array and predicted array.

    Parameters
    -----------
    pred_arr : `pandas.DataFrame` `numpy.ndarray` or array-like, shape (n_samples, n_outcomes)
        Array consisting of the `predicted values`. The dimensions of
        `pred_arr` are `n_samples` by `n_outcomes`, where `n_samples` is the
        number of observations, and `n_outcomes` the number of predicted
        outcomes.

    feat_arr : `numpy.ndarray`, `pandas.DataFrame` or array-like, shape (n_samples, n_features)
        Array consisting of the `predicted values`. The dimensions of
        `feat_arr` are `n_samples` by `n_features`, where `n_samples`
        is the number of observations, and `n_features` the number of
        features used.

    pre_opt : {'min_max', 'standard', 'normalize', 'no'} `str`, optional
        Type of preprocessing to do on `feat_arr`.

        Options:
            - 'min_max' : Turns `feat_arr` to values between (0,1)
            - 'standard' : Uses `sklearn.preprocessing.StandardScaler` method
            - 'normalize' : Uses the `sklearn.preprocessing.Normalizer` method
            - 'no' : No preprocessing on `feat_arr`

    shuffle_opt : `bool`, optional
        If True, the data is shuffled before splitting into testing and
        training datasets. This variable is set to True by default.

    random_state : int, optional
        Random state number used for when splitting into training and
        testing datasets. If set, it will always have the same seed
        `random_state`. This variable is set to `0` by default.

    test_size : float, optional
        Percentage of the catalogue that represents the `test` size of
        the testing dataset. This variable must be between (0,1).
        This variable is set to `0.25` by default.

    reshape : `bool`, optional
        If True, it reshapes `feat_arr` into a 1d array if its shapes is
        equal to (ncols, 1), where `ncols` is the number of columns.
        This variable is set to `False` by default.

    return_idx : `bool`, optional
        If `True`, it returns the indices of the `training` and `testing`
        datasets. This variable is set to `False` by default.

    Returns
    -----------
    train_dict : `dict`
        Dictionary containing the `training` data from the catalogue.

    test_dict : `dict`
        Dictionary containing the `testing` data from the catalogue.

    See also
    -----------
    data_preprocessing : Function to preprocess a dataset.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    # `pred_arr`
    pred_arr_type_valid = (list, np.ndarray, pd.DataFrame)
    if not (isinstance(pred_arr, pred_arr_type_valid)):
        msg = '{0} `pred_arr` ({1}) is not a valid input type'.format(
            file_msg, type(pred_arr))
        raise LSSUtils_Error(msg)
    # `feat_arr`
    feat_arr_type_valid = (list, np.ndarray, pd.DataFrame)
    if not (isinstance(feat_arr, feat_arr_type_valid)):
        msg = '{0} `feat_arr` ({1}) is not a valid input type'.format(
            file_msg, type(feat_arr))
        raise LSSUtils_Error(msg)
    # `pre_opt`
    pre_opt_valid = ['min_max', 'standard', 'normalize', 'no']
    if not (pre_opt in pre_opt_valid):
        msg = '{0} `pre_opt` ({1}) is not a valid input'.format(
            file_msg, pre_opt)
        raise LSSUtils_Error(msg)
    # `shuffle_opt`
    shuffle_opt_type_valid = (bool)
    if not (isinstance(shuffle_opt, shuffle_opt_type_valid)):
        msg = '{0} `shuffle_opt` ({1}) is not a valid input type'.format(
            file_msg, type(shuffle_opt))
        raise LSSUtils_Error(msg)
    # `random_state`
    random_state_type_valid = (int)
    if not (isinstance(random_state, random_state_type_valid)):
        msg = '{0} `random_state` ({1}) is not a valid input'.format(
            file_msg, random_state)
        raise LSSUtils_Error(msg)
    # `test_size`
    if not ((test_size > 0) and (test_size < 1.)):
        msg = '{0} `test_size` ({1}) must be in range (0,1)'.format(
            file_msg, test_size)
        raise LSSUtils_Error(msg)
    ##
    ## Checking indices of `pred_arr` and `feat_arr`
    if return_idx:
        # If object is a DataFrame
        if (    isinstance(pred_arr, pd.DataFrame) and
                isinstance(feat_arr, pd.DataFrame)):
            pred_arr_idx = pred_arr.index.values
            feat_arr_idx = feat_arr.index.values
        else:
            pred_arr_idx = np.arange(len(pred_arr))
            feat_arr_idx = np.arange(len(feat_arr))
        # Reshaping if necessary
        if reshape:
            pred_arr_idx = gu.reshape_arr_1d(pred_arr_idx)
            feat_arr_idx = gu.reshape_arr_1d(feat_arr_idx)
    ##
    ## Checking dimensions of `pred_arr` and `feat_arr`
    pred_arr = np.asarray(pred_arr)
    feat_arr = np.asarray(feat_arr)
    # Dimensions
    if reshape:
        pred_arr = gu.reshape_arr_1d(pred_arr)
        feat_arr = gu.reshape_arr_1d(feat_arr)
    # Shape
    if (len(pred_arr) != len(feat_arr)):
        msg  = '{0} The shape of `pred_arr` ({1}) and `feat_arr` ({2}) must '
        msg += 'have the same length'
        msg  = msg.format(file_msg, len(pred_arr), len(feat_arr))
        raise LSSUtils_Error(msg)
    ##
    ## Rescaling Dataset
    feat_arr_scaled = data_preprocessing(feat_arr, pre_opt=pre_opt,
        reshape=reshape)
    ##
    ## Splitting into `Training` and `Testing` datasets.
    # Scaled
    (   X_train, X_test,
        Y_train, Y_test) = skms.train_test_split(   feat_arr_scaled,
                                                    pred_arr,
                                                    test_size=test_size,
                                                    shuffle=shuffle_opt,
                                                    random_state=random_state)
    # Not-scaled
    (   X_train_ns, X_test_ns,
        Y_train_ns, Y_test_ns) = skms.train_test_split( feat_arr,
                                                        pred_arr,
                                                        test_size=test_size,
                                                        shuffle=shuffle_opt,
                                                        random_state=random_state)
    # Returning indices if necessary
    if return_idx:
        # Splitting to `training` and `testing`
        (   X_train_idx, X_test_idx,
            Y_train_idx, Y_test_idx) = skms.train_test_split(
                                                        feat_arr_idx,
                                                        pred_arr_idx,
                                                        test_size=test_size,
                                                        shuffle=shuffle_opt,
                                                        random_state=random_state)
        if not (np.array_equal(X_train_idx, Y_train_idx) and 
                np.array_equal(X_test_idx, Y_test_idx)):
            msg = '{0} Index arrays are not equal to each other!'
            raise LSSUtils_Error(msg)
    ##
    ## Assigning `training` and `testing` datasets to dictionaries
    # Saving indices if necessary
    if return_idx:
        # Adding 'indices' to dictionaries
        train_dict = {  'X_train': X_train, 'Y_train': Y_train,
                        'X_train_ns': X_train_ns, 'Y_train_ns': Y_train_ns,
                        'train_idx': X_train_idx}
        test_dict  = {'X_test': X_test, 'Y_test': Y_test,
                        'X_test_ns': X_test_ns, 'Y_test_ns': Y_test_ns,
                        'test_idx': X_test_idx}
    else:
        train_dict = {  'X_train': X_train, 'Y_train': Y_train,
                        'X_train_ns': X_train_ns, 'Y_train_ns': Y_train_ns}
        test_dict  = {'X_test': X_test, 'Y_test': Y_test,
                        'X_test_ns': X_test_ns, 'Y_test_ns': Y_test_ns}

    return train_dict, test_dict

# Scoring methods
def scoring_methods(truth_arr, feat_arr=None, pred_arr=None, model=None,
    score_method='perc', threshold=0.1, perc=0.68):
    """
    Determines the overall score for given arrays, i.e. the `predicted`
    array and the `truth` array

    Parameters
    -----------
    truth_arr : `numpy.ndarray` or array-like, shape (n_samples, n_outcomes)
        Array consisting of the `true` values for the `n_samples`
        observations. The dimensions of `truth_arr` are
        `n_samples` by `n_outcomes`, where `n_samples` is the
        number of observations, and `n_outcomes` the number of predicted
        outcomes.

    feat_arr : `numpy.ndarray`, array-like, or `NoneType`, shape (n_samples, n_features)
        Array consisting of the `predicted values`. The dimensions of
        `feat_arr` are `n_samples` by `n_features`, where `n_samples`
        is the number of observations, and `n_features` the number of
        features used. This variable is set to `None` by default.

    pred_arr : `numpy.ndarray`, array-like, or `NoneType`, shape (n_samples, n_outcomes)
        Array of predicted values from `feat_arr`. If ``model == None``,
        this variable must be an array-like object. If ``model != None``,
        this variable will not be used, and will be calculated using
        the `model` object. This variable is set to `None` by default.

    model : scikit-learn model object or `NoneType`
        Model used to estimate the score if ``score_method == 'model_score'``
        This variable is set to `None` by default.

    score_method : {'perc', 'threshold', 'model_score', 'r2'} `str`, optional
        Type of scoring to use when determining how well an algorithm
        is performing.

        Options:
            - 'perc' : Use percentage and rank-ordering of the values
            - 'threshold' : Score based on diffs of `threshold` or less from true value.
            - 'model_score' : Out-of-the-box metod from `sklearn` to determine success.
            - 'r2': R-squared statistic for error calcuation.

    threshold : float, optional
        Value to use when calculating the error within `threshold` value
        from the truth. This variable is set to `None` by default.
        If `None`, this variable assumes a value of `0.1`.

    perc : float, optional
        Value used when determining score within some `perc` percentile
        value form [0,1]. This variable is set to `None` by default.
        If `None`, it assumes a value of `0.68`.

    Returns
    -----------
    method_score : float
        Overall score from `pred_arr` to predict `truth_arr`.

    Notes
    -----------
    For more information on how to pre-process your data, see
    `http://scikit-learn.org/stable/modules/model_evaluation.html`_.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    # `feat_arr`
    feat_arr_type_valid = (list, np.ndarray, type(None))
    if not (isinstance(feat_arr, feat_arr_type_valid)):
        msg = '{0} `feat_arr` ({1}) is not a valid input type'.format(
            file_msg, type(feat_arr))
        raise LSSUtils_Error(msg)
    # `truth_arr`
    truth_arr_type_valid = (list, np.ndarray)
    if not (isinstance(truth_arr, truth_arr_type_valid)):
        msg = '{0} `truth_arr` ({1}) is not a valid input type'.format(
            file_msg, type(truth_arr))
        raise LSSUtils_Error(msg)
    # `score_method` - Type
    score_method_type_valid = (str)
    if not (isinstance(score_method, score_method_type_valid)):
        msg = '{0} `score_method` ({1}) is not a valid input type'.format(
            file_msg, type(score_method))
        raise LSSUtils_Error(msg)
    # `score_method` - Value
    score_method_valid = ['perc', 'threshold', 'model_score', 'r2']
    if not (score_method in score_method_valid):
        msg = '{0} `score_method` ({1}) is not a valid input!'.format(
            file_msg, score_method)
        raise LSSUtils_Error(score_method)
    # `threshold` - Type
    threshold_valid = (float, int)
    if not (isinstance(threshold, threshold_valid)):
        msg = '{0} `threshold` ({1}) is not a valid input type'.format(
            file_msg, type(threshold))
        raise LSSUtils_Error(msg)
    # `threshold` - Value
    if not (threshold >= 0.):
        msg = '{0} `threshold` ({1}) must be larger than 0!'.format(
            file_msg, threshold)
        raise LSSUtils_Error(msg)
    ##
    ## Checking for `model`, `pred_arr` and `feat_arr`
    # If both are none
    if ((model is None) and (pred_arr is None)):
        msg  = '{0} `model` and `pred_arr` cannot both be `None`. '
        msg += 'Only one can be `None`'
        msg  = msg.format(file_msg)
        raise LSSUtils_Error(msg)
    # If `feat_arr` and `pred_arr` are `None`
    if ((feat_arr is None) and (pred_arr is None)):
        msg = '{0} `feat_arr` and `pred_arr` cannot both be `None`'.format(
            file_msg)
        raise TypeError(msg)
    # `pred_arr` - Type
    # If both are `None`
    pred_arr_valid = ((list, np.ndarray))
    if (model is None):
        if not (isinstance(pred_arr, pred_arr_valid)):
            msg = '{0} `pred_arr` ({1}) is not a valid input type!'.format(
                file_msg, type(pred_arr))
            raise LSSUtils_Error(msg)
    ##
    ## Choosing scoring method
    # Percentile method
    if (score_method == 'perc'):
        # Checking for `pred_arr`
        if (pred_arr is None):
            pred_arr = model.predict(feat_arr)
        # Checking for `model`
        if (model is None):
            pred_arr = np.asarray(pred_arr)
        # Error calcualtion
        pred_err     = np.abs(pred_arr - truth_arr)
        method_score = scipy.stats.scoreatpercentile(pred_err, 100. * perc)
    # Threshold method
    if (score_method == 'threshold'):
        # Checking for `pred_arr`
        if (pred_arr is None):
            pred_arr = model.predict(feat_arr)
        # Checking for `model`
        if (model is None):
            pred_arr = np.asarray(pred_arr)
        # Error calcualtion
        pred_err     = np.abs(pred_arr - truth_arr)
        pred_thresh  = len(pred_err[pred_err <= threshold])
        method_score = pred_thresh / len(pred_arr)
    # R-squared method
    if (score_method == 'r2'):
        # Checking for `pred_arr`
        if (pred_arr is None):
            pred_arr = model.predict(feat_arr)
        # Checking for `model`
        if (model is None):
            pred_arr = np.asarray(pred_arr)
        # Error calcualtion
        method_score = skmetrics.r2_score(truth_arr, pred_arr)
    # Model method
    if (score_method == 'model_score'):
        method_score = model.score(feat_arr, truth_arr)

    return method_score
