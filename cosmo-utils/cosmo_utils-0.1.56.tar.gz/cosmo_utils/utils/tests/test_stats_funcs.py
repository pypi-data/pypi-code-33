#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-04-28
# Last Modified: 2018-04-28
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
"""
Set of test functions for the `stats_func` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.utils import stats_funcs

## Setting seed
seed = np.random.seed(0)
## Functions

##
## Testing `myceil` function
myceil_test = [ (12  , 10, 20.0),
                (13  , 1., 13.0),
                (14.5, 2., 16.0),
                (100 , 10, 100.0),
                (-90 , 10, -90),
                (-89.9, 10, -80),
                (12.05, 0.1, 12.1)]
@pytest.mark.parametrize('x, base, output', myceil_test)
def test_myceil(x, base, output):
    """
    Tests the function `cosmo_utils.utils.stats_funcs.myceil` for input and
    output parameters

    Parameters
    ----------
    x : float
        Number to be approximated to closest number to `base`

    base : float
        Base used to calculate the closest largest number

    output : float
        Closest float number to `x`, i.e. upper-bound float
    """
    myceil_out = stats_funcs.myceil(x, base)

    assert( pytest.approx(myceil_out, base) == output)

##
## Testing `myceil` function
myfloor_test = [(12   , 10 , 10.0 ),
                (13   , 1. , 13.0 ),
                (14.5 , 2. , 12.0 ),
                (99   , 20 , 80.0 ),
                (-90  , 10 , -90  ),
                (-89.9, 10 , -90.0),
                (12.05, 0.1, 12.0 )]
@pytest.mark.parametrize('x, base, output', myfloor_test)
def test_myfloor(x, base, output):
    """
    Tests the function `cosmo_utils.utils.stats_funcs.myceil` for input and
    output parameters

    Parameters
    ----------
    x : float
        Number to be approximated to closest number to `base`

    base : float
        Base used to calculate the closest largest number

    output : float
        Closest float number to `x`, i.e. upper-bound float
    """
    myceil_out = stats_funcs.myfloor(x, base)

    assert( pytest.approx(myceil_out, base) == output)

##
## Testing `Bins_array_create` function
bins_arr_test = [   ([1, 2, 3, 4, 5], 2, [0., 2., 4, 6.]),
                    ([1.2, 2.5, 3, 4], 0.8, [0.8, 1.6, 2.4, 3.2, 4.0]),
                    ([2.25, 3.4, 4.2, 4.3, 2.6], 2, [2., 4, 6.]),
                    ([-6, 2, -8.5, 3.], 3, [-9, -6, -3, 0, 3]),
                    ([1, 2, 3.5, 4], 2, [0., 2, 4.]),
                    ([-100, 200, 0. -12.5], 50., [-100, -50, 0., 50, 100, 150, 200])]
@pytest.mark.parametrize('arr, base, output', bins_arr_test)
def test_Bins_array_create(arr, base, output):
    """
    Tests the function `cosmo_utils.utils.stats_funcs.Bins_array_create` for
    input and output parameters

    Parameters
    -----------
    arr : array_like
        Array of of numbers or floats

    base : int or float, optional
        Interval used to create the evenly-spaced array of elements

    output : `numpy.ndarray`
        Array of elements separated in intervals of `base`
    """
    output = np.array(output)
    # Output from `Bins_array_create` function
    bins_arr = stats_funcs.Bins_array_create(arr, base)
    # Checking that array are equal
    assert(np.allclose(output, bins_arr))

##
## Testing `sigma_calcs`
sigma_calcs_test = [    (1, 100 , (1,100)),
                        (2, 1000, (2,100))]
@pytest.mark.parametrize('return_mean, out_type',[(True, tuple),(False, dict)])
@pytest.mark.parametrize('type_sigma',['std'])
@pytest.mark.parametrize('ndim, nelem, output', sigma_calcs_test)
def test_sigma_calcs_shape(ndim, nelem, output, type_sigma,
    return_mean, out_type):
    """
    Tests the function `cosmo_utils.utils.stats_funcs.sigma_calcs` for
    input and output parameters

    Parameters
    -----------
    ndim : int
        Dimesions of the array being tested

    nelem : int
        Number of elements in each sub-array

    output : tuple
        Tuple of elements

    type_sigma : {'std', 'perc'} str
        Type of statistics to use for the different sigmas/St. Dev.

    return_mean : `bool`
        If true, it returns `mean`, `std` and `sigmas`.
        If False, it only return `sigmas`.

    out_type : {list, dict} type object
        Type object for the given `return_mean` option
    """
    ## Unpacking input parameters
    ndim_out, len_out = output
    ## Generating dataset
    arr_test = np.random.random((ndim, nelem))
    ## Determining output from `sigma_calcs`
    dict_test      = stats_funcs.sigma_calcs(arr_test, type_sigma=type_sigma,
                        return_mean_std=False)
    dict_test_keys = dict_test.keys()
    ## Testing dimensions and lengths
    for ii in dict_test_keys:
        # Dimensions
        dict_ii_ndim = dict_test[ii].ndim
        assert(dict_ii_ndim == 2)
        # Lengths
        dict_ii_len  = len(dict_test[ii])
        assert(dict_ii_len == 2)
    ##
    ## Testing datatypes
    dict_test_all = stats_funcs.sigma_calcs(arr_test, type_sigma=type_sigma,
                        return_mean_std=return_mean)
    assert(type(dict_test_all) == out_type)
    # Testing types for when `return_mean` == 'True'
    if return_mean:
        assert(type(dict_test_all[0]) == dict)
        assert(type(dict_test_all[1]) == np.ndarray)
        assert(type(dict_test_all[2]) == np.ndarray)

##
## Testing `Stats_one_arr`
test_return_perc_arr     = [(True , 1),
                            (False, 0)]
arr_digit_expected_arr   = [('n', 4),
                            ('y', 6),
                            ('o', 2)]
test_stats_one_nelem_arr = [100, 1000, 10000, 50, 20]
@pytest.mark.parametrize('return_perc, return_perc_val', test_return_perc_arr)
@pytest.mark.parametrize('arr_digit, expected', arr_digit_expected_arr)
@pytest.mark.parametrize('nelem', test_stats_one_nelem_arr)
def test_Stats_one_arr_outputs(return_perc, return_perc_val, arr_digit,
    expected, nelem, bins=10, base=10):
    """
    Tests the function `cosmo_utils.utils.stats_funcs.Stats_one_arr` for
    input and output parameters

    Parameters
    ----------
    return_perc : `bool`, optional
        If true, it also returns the `percentiles` of the data.
        Last item in the return list.
        This variable is set to False by default.

    return_perc_val : int
        Value to add to `expected`, given if returning the percentiles
        of the bins or not.

    arr_digit : {'n', 'y', 'o'} str, optional
        Option for which elements to return.
        - 'n' : Returns `x1_stat`, `y1_stat`, `y1_std`, `y1_std_err`
        - 'y' : Returns `x1_stat`, `y1_stat`, `y1_std`, `y1_std_err`,
                        `x_bins_data`, `y_bins_data`
        - 'o' : Returns `x_bins_data`, `y_bins_data`

    expected : int
        Expected number of elements in the tuple, based on the input
        arguments

    nelem : int
        Size of the array. It will test if all of the elements are
        being returned correctly
    """
    ## Creating random arrays
    x = np.random.random(nelem) * 50.
    y = np.random.random(nelem) * 100.
    ##
    ## Running function
    output = stats_funcs.Stats_one_arr(x, y, base=base,
                arr_digit=arr_digit, statfunc=np.nanmean,
                return_perc=return_perc)
    ##
    ## Testing number of elements returned
    output_expected = expected + return_perc_val
    assert(len(output) == output_expected)
    ##
    ## Checking type of all of the returned items
    if return_perc:
        for ii in output[:-1]:
            assert(isinstance(ii, np.ndarray))
        assert(isinstance(output[-1], dict))
    else:
        for ii in output:
            assert(isinstance(ii, np.ndarray))
    ## Number of elements in array
    (   x_bins_data,
        y_bins_data) = stats_funcs.Stats_one_arr(x, y, base=base,
                        arr_digit='o', statfunc=np.nanmean, arr_len=0,
                        return_perc=False)
    assert(len(np.concatenate(x_bins_data).ravel()) == nelem)
    assert(len(np.concatenate(y_bins_data).ravel()) == nelem)
