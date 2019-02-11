#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-08
# Last Modified: 2018-05-08
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
"""
Set of test functions for the `abundance_matching` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.mock_catalogues import abundance_matching
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Test `reversed_arrays` - Inputs
reversed_arrays_input_arr = [   ([1,2,3,4], [10,15, 16, 20], True),
                                ([-5,-6,-7,-8], [-10,-11,-12,-20], False),
                                ([10,20,30],[-20,0, 20], True)]
@pytest.mark.parametrize('x, y, expected', reversed_arrays_input_arr)
def test_reversed_arrays(x, y, expected):
    """
    Tests the function 
    `cosmo_utils.mock_catalogues.abundance_matching.reversed_arrays`
    for input and output parameters.

    This function tests whether or not the 2 arrays are monotonically
    increasing with each other or not.

    Parameters
    ----------
    x : `numpy.ndarray`
        Array containing the 1st set of values

    y : `numpy.ndarray`
        Array containing the 2nd set of values.

    expected : `bool`
        If True, `x` increases monotonically with increasing `y`.
        If False, `x` decreases monotonically with increasing `y`.
    """
    ## Running function
    output = abundance_matching.reversed_arrays(x, y)
    ## Checking against expected value
    assert(output == expected)


