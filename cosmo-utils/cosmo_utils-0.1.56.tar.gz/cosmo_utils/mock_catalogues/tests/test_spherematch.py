#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-07
# Last Modified: 2018-05-07
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
"""
Set of test functions for the `spherematch` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.mock_catalogues import spherematch
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Testing `spherematch` function
def test_spherematch():
    """
    Tests the function 
    `cosmo_utils.mock_catalogues.spherematch.spherematch` for input and 
    output parameters.

    This function tests whether or not a catalogue is matched to 
    its shuffled version.
    """
    ## Initializing random catalogue
    ## Producing set of Right Ascension and Declination arrays
    ra_lim  = (  0, 360.)
    dec_lim = (-90,  90.)
    n_elem  = 1000
    # Right ascension and declination
    ra  = ra_lim [0] + np.random.random_sample(n_elem) * (ra_lim [1]-ra_lim [0])
    dec = dec_lim[0] + np.random.random_sample(n_elem) * (dec_lim[1]-dec_lim[0])
    # 1st sample
    sample1 = np.column_stack((ra, dec))
    # 2nd sample
    sample2 = sample1[:].copy()
    np.random.shuffle(sample2)
    ##
    ## Separating `ra1`, `dec1`, `ra2`, `dec2`
    ra1, dec1 = sample1.T
    ra2, dec2 = sample2.T
    ## Running function
    idx_s1, idx_s2, ds = spherematch.spherematch(   ra1,
                                                    dec1,
                                                    ra2,
                                                    dec2,
                                                    tol=0.01, nnearest=1,
                                                    nthreads=1)
    ## Comparing outcomes
    np.testing.assert_equal(sample1[idx_s1], sample2[idx_s2])
