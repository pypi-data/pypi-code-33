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
Set of test functions for the `mags_calculations` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.mock_catalogues import mags_calculations
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Testing `apparent_to_absolute_magnitude` function
app_abs_test_arr = [    (-0.72,  -3.1128 , 30.1  , 'pc'),
                        ( 0.14,  -7.0653 , 0.2761, 'kpc'),
                        ( 1.26,  -7.1945 , 0.4908, 'kpc'),
                        ( 6.00,  11.0    , 1     , 'pc'),
                        (-4.0 ,  -4.3959 , 12    , 'pc')]
@pytest.mark.parametrize('app_mag, abs_mag, lum_dist, unit', app_abs_test_arr)
def test_apparent_to_absolute_magnitude(app_mag, abs_mag, lum_dist, unit):
    """
    Tests the function 
    `cosmo_utils.mock_catalogues.mags_calculations.apparent_to_absolute_magnitude`
    for input and output parameters.

    This function tests whether or not the function recovers the 
    expected absolute magnitude.

    Parameters
    ----------
    app_mag : array_like
        Array of apparent magnitude(s)

    abs_mag : np.ndarray
        Array of absolute magnitudes. `abs_mag` is a float if 
        `app_mag` is a float or int.

    lum_dist : array_like
        Array of luminosity distnace to object. In units of `Mpc`.

    unit : {'pc', 'kpc', 'mpc'} str, optional
        Unit to use for `lum_dist`. This variable is set to `mpc` by
        default. When `pc`, the units are in parsecs, while `mpc` is for 
        distances in mega-parsecs, etc.
    """
    ## Calculations
    out_abs_mag = mags_calculations.apparent_to_absolute_magnitude(
        app_mag, lum_dist, unit=unit)
    ## Comparing to expected absolute distance
    np.testing.assert_almost_equal(abs_mag, out_abs_mag, decimal=1)

## Getting Sun's magnitudes
get_sun_mag_test_arr = [    ('U', 'Binney_and_Merrifield_1998', 5.61),
                            ('B', 'Binney_and_Merrifield_1998', 5.48),
                            ('V', 'Binney_and_Merrifield_1998', 4.83),
                            ('R', 'Binney_and_Merrifield_1998', 4.42),
                            ('I', 'Binney_and_Merrifield_1998', 4.08),
                            ('J', 'Binney_and_Merrifield_1998', 3.64),
                            ('H', 'Binney_and_Merrifield_1998', 3.32),
                            ('K', 'Binney_and_Merrifield_1998', 3.28),
                            ('u', 'SDSS_Blanton_2003_z0.1', 6.80),
                            ('g', 'SDSS_Blanton_2003_z0.1', 5.45),
                            ('r', 'SDSS_Blanton_2003_z0.1', 4.76),
                            ('i', 'SDSS_Blanton_2003_z0.1', 4.58),
                            ('z', 'SDSS_Blanton_2003_z0.1', 4.51)]
@pytest.mark.parametrize('filter_opt, system, expected', get_sun_mag_test_arr)
def test_get_sun_abs_mag(filter_opt, system, expected):
    """
    Tests the function 
    `cosmo_utils.mock_catalogues.mags_calculations.apparent_to_absolute_magnitude`
    for input and output parameters.

    This function tests whether or not the function recovers the 
    expected absolute magnitude.

    Parameters
    ----------
    filter: string
        magnitude filter to use.
    
    system: string
        Kind of filter to use. (default = `SDSS_Blanton_2003_z0.1`)
        Options: 
        - `Binney_and_Merrifield_1998`: See Binney and Merrifield 1998
        - `SDSS_Blanton_2003_z0.1`: See Blanton et al. 2003 equation 14

    expected : float
        Expected solar absolute magnitude in `filter` using `system`.
    """
    # Output from function
    out_sun_abs_mag = mags_calculations.get_sun_mag(filter_opt, system=system)
    # Comparing to expected absolute magnitude
    np.testing.assert_almost_equal(expected, out_sun_abs_mag)

