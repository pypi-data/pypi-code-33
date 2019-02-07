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
"""
Set of test functions for the `geometry` functions
"""

## Import modules
import numpy as np
import pandas as pd
import pytest
from   cosmo_utils.utils import geometry
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error


## Setting seed
seed = np.random.seed(0)

## Functions

## Testing function `flip_angles`
flip_angles_test_arr = [    (-50, 310.0),
                            (130.5, 130.5),
                            (-0.5, 359.5),
                            ([-10., -20.5, 60.], np.array([350.0, 339.5, 60.0])),
                            (np.array([12., -10]), np.array([12.0, 350.0]))]
@pytest.mark.parametrize('input_ang, output_ang', flip_angles_test_arr)
def test_flip_angles(input_ang, output_ang):
    """
    Tests the function `cosmo_utils.utils.geometry.flip_angles` for input and
    output parameters

    Parameters
    -----------
    input_ang : float, int, list, `numpy.ndarray`
        Input argument to evaluate

    output_ang : float, int, list, `numpy.ndarray`
        Result to test against. It is the expected result from `flip_angles`
        function.
    """
    ## Checking that outputs from function are the ones to be expected
    output_func = geometry.flip_angles(input_ang)
    # Checking agains 
    np.testing.assert_allclose(output_func, output_ang)

## Testing function Ang_Distance
def test_Ang_Distance_comparison_astropy():
    """
    Tests the function `cosmo_utils.utils.geometry.flip_angles` for input and
    output parameters.

    This method compares the values obtained from the `haversine` to those
    using the `astropy` method.
    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim  = (0, 360.)
    dec_lim = (-90, 90.)
    for ii in range(1, 1000, 10):
        ## Random array for RA and Dec
        ra1  = ra_lim[0]  + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec1 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ra2  = ra_lim[0]  + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec2 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ## Testing outputs from different methods
        out_haversine = geometry.Ang_Distance(ra1, ra2, dec1, dec2,
            method='haversine', unit='deg')
        out_astropy   = geometry.Ang_Distance(ra1, ra2, dec1, dec2,
            method='astropy', unit='deg')
        ## Checking that arrays are the same or similar
        np.testing.assert_allclose(out_haversine, out_astropy)

## Testing `Ang_Distance` for errors - Units
Ang_Distance_test_unit_arr = ['deg2', 'nan']
@pytest.mark.parametrize('unit', Ang_Distance_test_unit_arr)
def test_Ang_Distance_unit_errors(unit):
    """
    Tests the function `cosmo_utils.utils.geometry.flip_angles` for input and
    output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.

    Parameters
    -----------
    unit : {'dec','rad'} str, optional
        Unit of `ra1`, `ra2`, `dec1`, and `dec2`.
        This will also determine the final unit that outputs this function.

    method : {'haversine', 'astropy'} str, optional
        Method to use in order to calculate angular separation.
        This variable is to by default to the `haversine` method.
        If `astropy`, it will use the astropy framework to determine the
        angular separation.
    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim  = (  0, 360.)
    dec_lim = (-90,  90.)
    for ii in range(1, 1000, 10):
        ## Random array for RA and Dec
        ra1  = ra_lim [0] + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec1 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ra2  = ra_lim [0] + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec2 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ## Testing outputs from different methods
        # Haversine method
        with pytest.raises(LSSUtils_Error):
            out_astropy   = geometry.Ang_Distance(ra1, ra2, dec1, dec2,
                method='astropy', unit=unit)

## Testing `Ang_Distance` for errors - Method
Ang_Distance_test_method_arr = ['meter', 'NotMethod']
@pytest.mark.parametrize('method', Ang_Distance_test_method_arr)
def test_Ang_Distance_method_errors(method):
    """
    Tests the function `cosmo_utils.utils.geometry.flip_angles` for input and
    output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.

    Parameters
    -----------
    unit : {'dec','rad'} str, optional
        Unit of `ra1`, `ra2`, `dec1`, and `dec2`.
        This will also determine the final unit that outputs this function.

    method : {'haversine', 'astropy'} str, optional
        Method to use in order to calculate angular separation.
        This variable is to by default to the `haversine` method.
        If `astropy`, it will use the astropy framework to determine the
        angular separation.
    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim  = (  0, 360.)
    dec_lim = (-90,  90.)
    for ii in range(1, 1000, 10):
        ## Random array for RA and Dec
        ra1  = ra_lim [0] + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec1 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ra2  = ra_lim [0] + np.random.random_sample(ii) * (ra_lim [1]-ra_lim [0])
        dec2 = dec_lim[0] + np.random.random_sample(ii) * (dec_lim[1]-dec_lim[0])
        ## Testing outputs from different methods
        # Haversine method
        with pytest.raises(LSSUtils_Error):
            out_astropy = geometry.Ang_Distance(ra1, ra2, dec1, dec2,
                method=method, unit='deg')

## Testing `Coord_Transformation` for type of what it returns
Coord_test_return = [   (True, dict),
                        (False, pd.DataFrame)]
@pytest.mark.parametrize('return_dict, return_type', Coord_test_return)
def test_Coord_Transformation_types(return_dict, return_type):
    """
    Tests the function `cosmo_utils.utils.geometry.Coord_Transformation`
    for input and output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.
    """
    ## Expected keys in dict/DataFrame
    expected_keys = np.sort(['ra', 'dec', 'dist', 'x', 'y', 'z'])
    ## Producing set of Right Ascension and Declination arrays
    ra_lim   = (  0, 360.)
    dec_lim  = (-90,  90.)
    dist_lim = (1e-2, 100.)
    for ii in range(1000, 10000, 100):
        ## Random array for RA, DEC, and DIST
        # Centre
        ra_cen   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample()
        dec_cen  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample()
        dist_cen = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample()
        # Rest of elements
        ra   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample(ii)
        dec  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample(ii)
        dist = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample(ii)
        ##
        ## Generating outputs
        output = geometry.Coord_Transformation( ra,
                                                dec,
                                                dist,
                                                ra_cen,
                                                dec_cen,
                                                dist_cen,
                                                trans_opt=1,
                                                return_dict=return_dict)
        ## Checking return type
        assert(isinstance(output, return_type))
        ## Checking data returned
        if return_dict:
            output_keys = np.sort(list(output.keys()))
        else:
            output_keys = np.sort(output.columns.values)
        assert(np.array_equal(expected_keys, output_keys))
        ##
        ## Checking sizes
        for elem in expected_keys:
            assert(len(output[elem]) == ii)

## Testing `Coord_Transformation` for errors - Units
Coord_test_unit_errors = ['nan', 'NotDegree']
@pytest.mark.parametrize('unit', Coord_test_unit_errors)
def test_Coord_Transformation_errors(unit):
    """
    Tests the function `cosmo_utils.utils.geometry.Coord_Transformation`
    for input and output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.

    Parameters
    ----------
    unit : {'dec','rad'} str, optional
        Unit of `ra1`, `ra2`, `dec1`, and `dec2`.
        This will also determine the final unit that outputs this function.
        This variable is set to `deg` by default.


    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim   = (  0, 360.)
    dec_lim  = (-90,  90.)
    dist_lim = (1e-2, 100.)
    for ii in range(1000, 10000, 100):
        ## Random array for RA, DEC, and DIST
        # Centre
        ra_cen   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample()
        dec_cen  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample()
        dist_cen = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample()
        # Rest of elements
        ra   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample(ii)
        dec  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample(ii)
        dist = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample(ii)
        ##
        ## Generating outputs
        with pytest.raises(LSSUtils_Error):
            output = geometry.Coord_Transformation( ra,
                                                    dec,
                                                    dist,
                                                    ra_cen,
                                                    dec_cen,
                                                    dist_cen,
                                                    trans_opt=1,
                                                    return_dict=True,
                                                    unit=unit)

## Testing `Coord_Transformation` for errors - trans_opt
Coord_test_trans_opt_errors = list(range(5, 10))
@pytest.mark.parametrize('trans_opt', Coord_test_trans_opt_errors)
def test_Coord_Transformation_errors(trans_opt):
    """
    Tests the function `cosmo_utils.utils.geometry.Coord_Transformation`
    for input and output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.

    Parameters
    ----------
    trans_opt : {1, 2, 3, 4} int, optional
        Option for cartesian translation/transformation for elements.
        This variable ist set to `4` by default.

        Options:
            - 1 : No translation involved
            - 2 : Translation to the center point.
            - 3 : Translation `and` rotation to the center point.
            - 4 : Translation and 2 rotaitons about the center point

    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim   = (  0, 360.)
    dec_lim  = (-90,  90.)
    dist_lim = (1e-2, 100.)
    for ii in range(1000, 10000, 100):
        ## Random array for RA, DEC, and DIST
        # Centre
        ra_cen   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample()
        dec_cen  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample()
        dist_cen = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample()
        # Rest of elements
        ra   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample(ii)
        dec  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample(ii)
        dist = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample(ii)
        ##
        ## Generating outputs
        with pytest.raises(LSSUtils_Error):
            output = geometry.Coord_Transformation( ra,
                                                    dec,
                                                    dist,
                                                    ra_cen,
                                                    dec_cen,
                                                    dist_cen,
                                                    trans_opt=trans_opt,
                                                    return_dict=True,
                                                    unit='deg')

## Testing `Coord_Transformation` for errors - ra_cen type
Coord_test_ra_cen_errors = ['1', 'String']
@pytest.mark.parametrize('ra_cen', Coord_test_ra_cen_errors)
def test_Coord_Transformation_errors(ra_cen):
    """
    Tests the function `cosmo_utils.utils.geometry.Coord_Transformation`
    for input and output parameters.

    This function makes sure that errors are raised whenever a wrong
    input is given.

    Parameters
    ----------
    ra_cen : float, int
        Right Ascension, declination, and distance for the center of
        the coordinates. These correspond to where the corodinates
        `ra`, `dec`, and `dist` will be centered.

    """
    ## Producing set of Right Ascension and Declination arrays
    ra_lim   = (  0, 360.)
    dec_lim  = (-90,  90.)
    dist_lim = (1e-2, 100.)
    for ii in range(1000, 10000, 100):
        ## Random array for RA, DEC, and DIST
        # Centre
        dec_cen  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample()
        dist_cen = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample()
        # Rest of elements
        ra   = ra_lim  [0] + (ra_lim  [1]-ra_lim  [0]) * np.random.random_sample(ii)
        dec  = dec_lim [0] + (dec_lim [1]-dec_lim [0]) * np.random.random_sample(ii)
        dist = dist_lim[0] + (dist_lim[1]-dist_lim[0]) * np.random.random_sample(ii)
        ##
        ## Generating outputs
        with pytest.raises(LSSUtils_Error):
            output = geometry.Coord_Transformation( ra,
                                                    dec,
                                                    dist,
                                                    ra_cen,
                                                    dec_cen,
                                                    dist_cen,
                                                    trans_opt=1,
                                                    return_dict=True,
                                                    unit='deg')
