#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-07
# Last Modified: 2018-05-07
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "abundance_matching_f",
                    "reversed_arrays"]

# Importing modules
import numpy as np
from   scipy.interpolate import interp1d
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

# Functions

# Reversed arrays
def reversed_arrays(x, y):
    """
    Determines if arrays increase or decrease monotonically.

    Parameters
    -----------
    x : `numpy.ndarray`
        Array containing the 1st set of values

    y : `numpy.ndarray`
        Array containing the 2nd set of values.

    Return
    -----------
    mono_opt : `bool`
        If True, `x` increases monotonically with increasing `y`.
        If False, `x` decreases monotonically with increasing `y`.

    Raises
    ----------
    LSSUtils_Error : Exception
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    # Testing input arguments
    # x-array
    valid_types = (list, np.ndarray)
    if not (isinstance(x, valid_types)):
        msg = '{0} `x` is not a valid type!'.format(file_msg, type(x))
        raise LSSUtils_Error(msg)
    # y-array
    valid_types = (list, np.ndarray)
    if not (isinstance(y, valid_types)):
        msg = '{0} `y` is not a valid type!'.format(file_msg, type(y))
        raise LSSUtils_Error(msg)
    # x- and y-array shapes
    x = np.asarray(x)
    y = np.asarray(y)
    #
    # Checking if arrays increase or decrease monotonically
    x_diff = np.diff(x).sum()
    y_diff = np.diff(y).sum()
    # Monotonically increasing or decreasing
    if (x_diff > 0) and (y_diff > 0):
        mono_opt = True
    else:
        mono_opt = False

    return mono_opt

## Abundance Matching function
def abundance_matching_f(dict1, dict2, volume1=1., volume2=1., reverse=True,
    dens1_opt=False):
    """
    Abundance matching based on 2 quantities.
    It assigns values from `dict2` to elements in `dict1`

    Parameters
    -----------
    dict1 : python dictionary or `numpy.ndarray`
        Dictionary or array of 1st property.

        Keys :
            - `var` : 1st variable to be analysed
            - `dens` : Density array corresponding to `var` elements.
                        Only if `dens` == True.

    dict2 : python dictionary
        dictionary or array of the 2nd property.

        Keys :
            - `var` : 2nd variable to be analyzed
            - `dens` : Density array corresponding to `var` elements.
                        Given if `dens` == True.

    volume1 : float
        Corresponding volume to `dict1`.

    reverse : `bool`, optional
        Determines the relation between `var1` and `var2`.

    dens1_opt : `bool`, optional
        If True, `density` must be calculated.

        Options :
            - `True` : Density is already provided as key for `dict1`.
            - `False` : Density must be calculated.

    Returns
    -----------
    var1_ab : `numpy.ndarray`
        Array of elements matching those of `dict1`, after matching with
        `dict2`.
    """
    file_msg = fd.Program_Msg(__file__)
    # Check types of input paramenters
    valid_types = (list, dict, np.ndarray)
    # `dict1`
    if not (isinstance(dict1, valid_types)):
        msg = '{0} `dict1` ({1}) is not a valid type!'.format(file_msg,
            type(dict1))
    # `dict2`
    if not (isinstance(dict2, dict)):
        msg = '{0} `dict2` must be a dictionary. Its type is `{1}`'.format(
            file_msg, type(dict2))
        raise LSSUtils_Error(msg)
    # 2nd property
    var2  = np.asarray(dict2['var' ])
    dens2 = np.asarray(dict2['dens'])
    #
    # `dens1_opt`
    if dens1_opt:
        # 1st Property
        var1   = np.asarray(dict1['var' ])
        dens_1 = np.asarray(dict1['dens'])
    else:
        if (isinstance(dict1, dict)):
            var1 = dict1['var']
        elif (isinstance(dict1, (list, np.ndarray))):
            var1 = dict1.copy()
        #
        # Determining relation between `var1` and `var2`
        mono_opt_1 = reversed_arrays(var1, var2)
        # Monotonically increasing
        if mono_opt_1:
            counts_1 = np.array([np.where(var1 > x)[0].size for x in var1]) + 1
        else:
            counts_1 = np.array([np.where(var1 < x)[0].size for x in var1]) + 1
        #
        # Determining density of 1st property
        dens_1 = counts_1.astype(float) / volume1
    #
    # Interpolation for 2nd property
    var2_interp = interp1d(dens2, var2, bounds_error=True, assume_sorted=False)
    # Assigning values to property 1
    var1_ab = np.asarray([var2_interp(xx) for xx in dens_1])

    return var1_ab
