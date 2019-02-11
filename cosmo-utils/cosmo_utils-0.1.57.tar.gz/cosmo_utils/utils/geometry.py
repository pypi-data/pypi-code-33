#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-03
# Last Modified: 2018-05-03
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "flip_angles",
                    "Ang_Distance",
                    "Coord_Transformation"]
"""
Set of geometrical definitions for translations, coordinate tranformations,
etc.
"""

## Import modules
import numpy as np
import pandas as pd
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

# Restricting angles to be between 0 and 360
def flip_angles(ang, unit='deg'):
    """
    Ensures that an angle is always between 0 and 360 degrees.

    Parameters
    ----------
    ang : float, int, `numpy.ndarray`
        Angle in units of degrees.

    unit : {'deg', 'rad'} str, optional
        Unit of the angle. This variable is set to 'deg' by default.
        If 'rad', the output will be in units of radians.

    Returns
    ----------
    ang_out : float
        Convertions of `ang`, ranging from 0 to 360 degrees.

    Raises
    ----------
    LSSUtils_Error : Exception
        This error gets raised when `ang` is not a digit or a number.

    Examples
    ----------
    >>> flip_angles(-50, unit='deg')
    310.0

    >>> flip_angles(110, unit='deg')
    110.0
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking type of `ang`
    valid_types = (float, int, list, np.ndarray)
    if not (isinstance(ang, valid_types)):
        msg = '{0} `ang` ({1}) is not a number! Exiting!'.format(
            file_msg, ang)
        raise LSSUtils_Error(msg)
    # Checking `unit`
    if not (unit.lower() in ['deg', 'rad']):
        msg = '{0} `unit` ({1}) is not a valid option! Exiting!'.format(
            file_msg, unit)
        raise LSSUtils_Error(msg)
    ##
    ## Converting angle
    if isinstance(ang, float) or isinstance(ang, int):
        ang = float(ang)
        # Converting from radians to degrees, if applicable
        if unit == 'rad':
            ang_converted = np.degrees(ang)
        elif unit == 'deg':
            ang_converted = ang
        # Checking the range of `ang`
        if ang_converted < 0:
            ang_converted += 360
        # Converting back to radians, if applicable
        if unit == 'rad':
            ang_final = np.radians(ang_converted)
        elif unit == 'deg':
            ang_final = float(ang_converted)
    else:
        try:
            ang = np.asarray(ang)
            # Converting to degrees, if applicable
            if unit == 'rad':
                ang_converted = np.degrees(ang)
            elif unit == 'deg':
                ang_converted = ang
            # Checking the range of `ang`
            ang_converted = np.asarray([xx if xx > 0 else xx+360 for xx in
                ang_converted])
            # Converting back to radians, if applicable
            if unit == 'rad':
                ang_final = np.radians(ang_converted)
            elif unit == 'deg':
                ang_final = ang_converted
            # Converting to float
            ang_final = ang_final.astype(float)
        except:
            msg = '{0} `ang` could not be converted!'.format(file_msg)
            raise LSSUtils_Error(msg)

    return ang_final

## Calculates the Angular distance between 2 points
def Ang_Distance(ra1, ra2, dec1, dec2, unit='deg', method='haversine'):
    """
    Calculates angular separation between two sets of points with given
    right ascensions and declinations.

    Taken from: https://en.wikipedia.org/wiki/Haversine_formula

    Parameters
    -----------
    ra1, ra2 : float
        Right Ascension of the 1st and 2nd points. Units in `degrees`
        by default.

    dec1, dec2 : float
        Declination of the 1st and 2nd points. Units in `degrees` by default.

    unit : {'dec','rad'} str, optional
        Unit of `ra1`, `ra2`, `dec1`, and `dec2`.
        This will also determine the final unit that outputs this function.

    method : {'haversine', 'astropy'} str, optional
        Method to use in order to calculate angular separation.
        This variable is to by default to the `haversine` method.
        If `astropy`, it will use the astropy framework to determine the
        angular separation.

    Returns
    -----------
    ang_sep : float
        Angular separation between 1st and 2nd point.
        In units of `degrees`.

    Notes
    -----------
    A = 90. - `dec2`
    B = 90. - `dec1`
    D = `ra1` - `ra2`
    c = Angle between two points
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input arguments
    # Valid options
    units_valid   = ['deg', 'rad']
    methods_valid = ['haversine', 'astropy']
    # Units
    if not (unit in units_valid):
        msg = '{0} `unit` ({1}) is not a valid argument'.format(
            file_msg, unit)
        raise LSSUtils_Error(msg)
    # Method
    if not (method in methods_valid):
        msg = '{0} `method` ({1}) is not a valid argument'.format(
            file_msg, method)
        raise LSSUtils_Error(msg)
    ##
    ## Flipping angles
    ra1 = flip_angles(ra1, unit=unit, )
    ra2 = flip_angles(ra2, unit=unit)
    ##
    ## Haversine Method
    if method == 'haversine':
        A = np.radians(90. - dec1)
        B = np.radians(90. - dec2)
        D = np.radians(ra1 - ra2 )
        # Distance
        ang_sep  = (np.sin((A - B) * .5))**2.
        ang_sep += np.sin(A) * np.sin(B) * (np.sin(D * .5))**2.
        ang_sep  = np.degrees(2 * np.arcsin(ang_sep**0.5))
    ##
    ## Astropy Method
    if method == 'astropy':
        # Imports
        from astropy.coordinates import SkyCoord
        from astropy import units as u
        # Converting to `units`
        if unit == 'deg':
            unit_opt = u.degree
        elif unit == 'rad':
            unit_opt = u.radians
        # Calculations
        p1 = SkyCoord(ra=ra1, dec=dec1, unit=(unit_opt, unit_opt))
        p2 = SkyCoord(ra=ra2, dec=dec2, unit=(unit_opt, unit_opt))
        # Angular Separation
        ang_sep = p1.separation(p2)
        # Converting to final units
        if unit == 'deg':
            ang_sep = ang_sep.degree
        elif unit == 'rad':
            ang_sep = ang_sep.radians

    return ang_sep

## Coordinate Transformation function
def Coord_Transformation(ra, dec, dist, ra_cen, dec_cen, dist_cen,
    trans_opt=4, return_dict=False, unit='deg'):
    """
    Transforms spherical coordinates (ra, dec, dist) into cartesian
    coordinates.

    Parameters
    -----------
    ra, dec, dist : array_like, shape (N,)
        Arrays of Right Ascension, declination, and distance.
        Units are ['degrees', 'degrees', 'distance_units']

    ra_cen, dec_cen, dist_cen : float, int
        Right Ascension, declination, and distance for the center of
        the coordinates. These correspond to where the corodinates
        `ra`, `dec`, and `dist` will be centered.

    trans_opt : {1, 2, 3, 4} int, optional
        Option for cartesian translation/transformation for elements.
        This variable ist set to `4` by default.

        Options:
            - 1 : No translation involved
            - 2 : Translation to the center point.
            - 3 : Translation `and` rotation to the center point.
            - 4 : Translation and 2 rotaitons about the center point

    return_dict : {True, False}, `bool`, optional
        If `True`, this functions returns 2 dictionaries with `spherical`
        and `cartesian` coordinates.
        If `False`, it returns a `pandas.DataFrame` with the columns.
        This variable is set to `False` by default.

    unit : {'dec','rad'} str, optional
        Unit of `ra1`, `ra2`, `dec1`, and `dec2`.
        This will also determine the final unit that outputs this function.
        This variable is set to `deg` by default.

    Returns
    -----------
    coord_dict (coord_pd) : python dictionary
        Dictionary with spherical and cartesian dictionary of elements
        based on `trans_opt` value. This value is returned if
        `return_dict` is set to `True`. If not, a `pandas.DataFrame` is
        return.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Check types of elements
    # Units
    unit_arr = ['deg', 'rad']
    if not (unit in unit_arr):
        '{0} `unit` ({1}) is not a valid input!'.format(
            file_msg, unit)
    # Valid types
    valid_types = (float, int, np.ndarray, list)
    # Right Ascension
    if not (isinstance(ra, valid_types)):
        msg = '{0} `ra` ({1}) is not a valid type!'.format(
            file_msg, type(ra))
        raise LSSUtils_Error(msg)
    # Declination
    if not (isinstance(dec, valid_types)):
        msg = '{0} `dec` ({1}) is not a valid type!'.format(
            file_msg, type(dec))
        raise LSSUtils_Error(msg)
    # Distance
    if not (isinstance(dist, valid_types)):
        msg = '{0} `dist` ({1}) is not a valid type!'.format(
            file_msg, type(dist))
        raise LSSUtils_Error(msg)
    # trans_opt
    if not (trans_opt in list(range(1, 5))):
        msg = '{0} `trans_opt` ({1}) is not within valid range!'.format(
            file_msg, trans_opt)
        raise LSSUtils_Error(msg)
    ##
    ## Centre's RA, DEC, DIST
    # Right Ascension
    if (isinstance(ra_cen, float)):
        ra_cen = flip_angles(ra_cen)
    else:
        msg = '{0} `ra_cen` ({1}) is not a float!'.format(
            file_msg, type(ra_cen))
        raise LSSUtils_Error(msg)
    # Declination
    if (isinstance(dec_cen, float)):
        dec_cen = flip_angles(dec_cen)
    else:
        msg = '{0} `dec_cen` ({1}) is not a float!'.format(
            file_msg, type(dec_cen))
        raise LSSUtils_Error(msg)
    # Distance
    if (isinstance(dist_cen, float)):
        dist_cen = float(dist_cen)
    else:
        msg = '{0} `dist_cen` ({1}) is not a float!'.format(
            file_msg, type(dist_cen))
        raise LSSUtils_Error(msg)
    ##
    ## Check type of elements
    # Right Ascension
    if (isinstance(ra, float) or isinstance(ra, int)):
        ra = np.array([ra])
    else:
        ra = np.array(ra)
    # Declination
    if (isinstance(dec, float) or isinstance(dec, int)):
        dec = np.array([dec])
    else:
        dec = np.array(dec)
    # Distance
    if (isinstance(dist, float) or isinstance(dist, int)):
        dist = np.array([dist])
    else:
        dist = np.array(dist)
    ##
    ## Converting to desired units
    if unit == 'rad':
        # Right Ascension
        ra_rad     = ra
        ra_cen_deg = np.degrees(ra_cen)
        ra_cen_rad = ra_cen
        # Declination
        dec_rad     = dec
        dec_cen_deg = np.degrees(dec_cen)
        dec_cen_rad = dec_cen
    elif unit == 'deg':
        ra_rad     = np.radians(ra)
        ra_cen_deg = ra_cen
        ra_cen_rad = np.radians(ra_cen)
        # Declination
        dec_rad     = np.radians(dec)
        dec_cen_deg = dec_cen
        dec_cen_rad = np.radians(dec_cen)
    ##
    ## Initializing pandas DataFrame
    dict_keys  = ['ra', 'dec', 'dist']
    coord_dict = dict(zip(dict_keys, np.vstack([ra, dec, dist])))
    ##
    ## Spherical to Cartesian transformation
    ## 1st tranformation
    # Centre
    x_cen = dist_cen * np.cos(ra_cen_rad) * np.cos(dec_cen_rad)
    y_cen = dist_cen * np.sin(ra_cen_rad) * np.cos(dec_cen_rad)
    z_cen = dist_cen * np.sin(dec_cen_rad)
    # All galaxies
    x = dist * np.cos(ra_rad) * np.cos(dec_rad)
    y = dist * np.sin(ra_rad) * np.cos(dec_rad)
    z = dist * np.sin(dec_rad)
    ##
    ## Rotations about z- and x-axis by `tau` and `Omega`
    ## Rotating the points, not the axes
    x1 = x - x_cen
    y1 = y - y_cen
    z1 = z - z_cen
    # Angles
    omega = np.radians(90. - ra_cen_deg )
    tau   = np.radians(90. - dec_cen_deg)
    # Rotations about z-axis by `omega`
    x2 = x1 * np.cos(omega) - y1 * np.sin(omega)
    y2 = x1 * np.sin(omega) + y1 * np.cos(omega)
    z2 = z1.copy()
    # Rotations about X-axis by `tau`
    x3 = x2.copy()
    y3 = y2 * np.cos(tau) - z2 * np.sin(tau)
    z3 = z2 * np.sin(tau) + z2 * np.cos(tau)
    ##
    ## Definining which variables to return
    # No Translation
    if trans_opt == 1:
        coord_dict['x'] = x
        coord_dict['y'] = y
        coord_dict['z'] = z
    # Translation
    if trans_opt == 2:
        coord_dict['x'] = x1
        coord_dict['y'] = y1
        coord_dict['z'] = z1
    # Translation + Rotation
    if trans_opt == 3:
        coord_dict['x'] = x2
        coord_dict['y'] = y2
        coord_dict['z'] = z2
    # Translation + 2 Rotation (centered about the centre)
    if trans_opt == 4:
        coord_dict['x'] = x3
        coord_dict['y'] = y3
        coord_dict['z'] = z3
    ##
    ## Checking what object to return, i.e. DataFrame or python dictionary
    if return_dict:
        return coord_dict
    else:
        coord_pd = pd.DataFrame(coord_dict)
        return coord_pd

## Coordinate Transformation - Cartesian to Spherical coordinates
def cart_to_sph_coords(dist, x_arr, y_arr, z_arr, return_dict=False,
    unit='deg'):
    """
    Transforms cartesian coordinates (x, y, z) into spherical
    coordinates.

    Parameters
    -----------
    dist : `np.ndarray`
        Array of the the distance to the N-number of objects.
        Shape (N,).

    x_arr, y_arr, z_arr : `np.ndarray`
        Arrays of the cartesian coordinates (x, y, z) of the
        N objects. Shape (N,). Units are in `unit`.

    return_dict : {True, False}, `bool`, optional
        If `True`, this functions returns 2 dictionaries with `spherical`
        and `cartesian` coordinates.
        If `False`, it returns a `pandas.DataFrame` with the columns.
        This variable is set to `False` by default.

    unit : {'dec','rad'} `str`, optional
        Unit of the output `ra`, `dec` coordinates.
        This variable is set to `deg` by default.

    Returns
    -----------
    coord_dict (coord_pd) : `dict`
        Dictionary with spherical coordinates (`ra`, `dec`) and
        distance (`dist`) of N elements. This value is returned if
        `return_dict` is set to `True`. If not, a `pd.DataFrame` is
        returned.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Check types of elements
    # Units
    unit_arr = ['deg', 'rad']
    if not (unit in unit_arr):
        '{0} `unit` ({1}) is not a valid input!'.format(
            file_msg, unit)
    # Valid types
    valid_types = (float, int, np.ndarray, list)
    # X-coordinate
    if not (isinstance(x_arr, valid_types)):
        msg = '{0} `x_arr` ({1}) is not a valid type!'.format(
            file_msg, type(x_arr))
        raise LSSUtils_Error(msg)
    # Y-coordinate
    if not (isinstance(y_arr, valid_types)):
        msg = '{0} `y_arr` ({1}) is not a valid type!'.format(
            file_msg, type(y_arr))
        raise LSSUtils_Error(msg)
    # Z-coordinate
    if not (isinstance(z_arr, valid_types)):
        msg = '{0} `z_arr` ({1}) is not a valid type!'.format(
            file_msg, type(z_arr))
        raise LSSUtils_Error(msg)
    # Distance
    if not (isinstance(dist, valid_types)):
        msg = '{0} `dist` ({1}) is not a valid type!'.format(
            file_msg, type(dist))
        raise LSSUtils_Error(msg)
    ##
    ## Check type of elements
    # X-Coordinate
    if (isinstance(x_arr, float) or isinstance(x_arr, int)):
        x_arr = np.array([x_arr])
    else:
        x_arr = np.array(x_arr)
    # Y-Coordinate
    if (isinstance(y_arr, float) or isinstance(y_arr, int)):
        y_arr = np.array([y_arr])
    else:
        y_arr = np.array(y_arr)
    # Z-Coordinate
    if (isinstance(z_arr, float) or isinstance(z_arr, int)):
        z_arr = np.array([z_arr])
    else:
        z_arr = np.array(z_arr)
    # Distance
    if (isinstance(dist, float) or isinstance(dist, int)):
        dist = np.array([dist])
    else:
        dist = np.array(dist)
    ##
    ## Initializing pandas DataFrame
    dict_keys  = ['x', 'y', 'z', 'dist']
    coord_dict = dict(zip(dict_keys, np.vstack([x_arr, y_arr, z_arr, dist])))
    ##
    ## Cartesian to Spherical coordinates
    ##
    ## - Normalized cartesian coordinates
    cart_arr = np.column_stack([x_arr, y_arr, z_arr])





    (   x_val,
        y_val,
        z_val) = cart_arr/float(dist)
    # Distance to object
    dist = float(dist)
    ## Declination
    dec_val = 90. - num.degrees(num.arccos(z_val))
    ## Right ascension
    if x_val == 0:
        if y_val > 0.:
            ra_val = 90.
        elif y_val < 0.:
            ra_val = -90.
    else:
        ra_val = num.degrees(num.arctan(y_val/x_val))
    ##
    ## Seeing on which quadrant the point is at
    if x_val < 0.:
        ra_val += 180.
    elif (x_val >= 0.) and (y_val < 0.):
        ra_val += 360.

    return ra_val, dec_val
