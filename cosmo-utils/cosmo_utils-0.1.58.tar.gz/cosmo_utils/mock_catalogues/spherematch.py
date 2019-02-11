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
__all__        = [  "spherematch"]

## Import modules
import math
import numpy as np
from   scipy.spatial import cKDTree as KDT
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Spherical to Cartesian - Normal version
def _spherical_to_cartesian(ra, dec):
    """
    Converts spherical coordinates (ra, dec) to cartesian coordinates (x,y,z).

    Parameters
    ----------
    ra, dec : array_like
        Right Ascension and Declination of the object. Units in `degrees`.

    Returns
    ----------
    x, y, z : array_like
        Cartesian coordinates of the object
    """
    # Converting to radians
    ra_arr  = np.radians(ra )
    dec_arr = np.radians(dec)
    # Cartesian coordinates
    x = np.cos(ra_arr) * np.cos(dec_arr)
    y = np.sin(ra_arr) * np.cos(dec_arr)
    z = np.sin(dec_arr)

    return x, y, z

## Spherical to Cartesian - Fast version
def _spherical_to_cartesian_fast(ra, dec, nthreads):
    """
    Converts spherical coordinates (ra, dec) to cartesian coordinates (x,y,z).

    Parameters
    ----------
    ra, dec : array_like
        Right Ascension and Declination of the object. Units in `degrees`

    nthreads : int
        Number of threads to use for calculation

    Returns
    ----------
    x, y, z : array_like
        Cartesian coordinates of the object

    Notes
    ----------
    This is a `fast` version of converting between spherical and
    cartesian coordinates.
    """
    # Importing 'numexpr'
    import numexpr as ne
    # Constants
    pi = math.pi
    # Setting number of Threads
    ne.set_num_threads(nthreads)
    # Evaluating arrays
    ra_arr  = ne.evaluate('ra*pi/180.0')
    dec_arr = ne.evaluate('dec*pi/180.0')
    hold1   = ne.evaluate('cos(dec_arr)')
    # Cartesian coordinates
    x = ne.evaluate('cos(ra_arr) * hold1')
    y = ne.evaluate('sin(ra_arr) * hold1')
    z = ne.evaluate('sin(dec_arr)')

    return x, y, z

## Great Circle - Normal version
def _great_circle_distance(ra1, dec1, ra2, dec2):
    """
    Computes the `great circle distance` between two points.

    Parameters
    ----------
    ra1, dec1 : array_like
        Right Ascension and Declination of the 1st point.
        Units in `degrees`.

    ra2, dec2 : array_like
        Right Ascension and Declination of the 2nd point.
        Units in `degrees`.

    Returns
    ----------
    great_circle_dist : float
        Great Circle distance between the 1st and 2nd location

    Notes
    ----------
    This function uses a vincenty distance.
    For more information see:
        https://en.wikipedia.org/wiki/Vincenty%27s_formulae

    It is a bit slower than others, but numerically stable.
    """
    # Importing modules
    from numpy import degrees, sin, cos, arctan2, hypot
    ##
    ## Terminology from the Vincenty Formula - `lambda` and `phi` and
    ## `standpoint` and `forepoint`
    lambs = np.radians(ra1 )
    phis  = np.radians(dec1)
    lambf = np.radians(ra2 )
    phif  = np.radians(dec2)
    # Calculations
    dlamb = lambf - lambs
    ## Constants for evaluation
    # Calculate these ones instead of few times!
    numera = cos(phif) * sin(dlamb)
    numerb = cos(phis) * sin(phif) - sin(phis) * cos(phif) * cos(dlamb)
    numer  = hypot(numera, numerb)
    denom  = sin(phis) * sin(phif) + cos(phis) * cos(phif) * cos(dlamb)
    # Great Circle Distance
    great_circle_dist = degrees(arctan2(numer, denom))

    return great_circle_dist

## Great Circle - Fast version
def _great_circle_distance_fast(ra1, dec1, ra2, dec2, nthreads):
    """
    Computes the `great circle distance` between two points.

    Parameters
    ----------
    ra1, dec1 : array_like
        Right Ascension and Declination of the 1st point.
        Units in `degrees`.

    ra2, dec2 : array_like
        Right Ascension and Declination of the 2nd point.
        Units in `degrees`.

    nthreads : int
        Number of threads to use for calculation

    Returns
    ----------
    great_circle_dist : float
        Great Circle distance between the 1st and 2nd location

    Notes
    ----------
    This function uses a vincenty distance.
    For more information see:
        https://en.wikipedia.org/wiki/Vincenty%27s_formulae

    It is a bit slower than others, but numerically stable.
    """
    import numexpr as ne
    ##
    ## Terminology from the Vincenty Formula - `lambda` and `phi` and
    ## `standpoint` and `forepoint`
    lambs = np.radians(ra1 )
    phis  = np.radians(dec1)
    lambf = np.radians(ra2 )
    phif  = np.radians(dec2)
    # Calculations
    dlamb = lambf - lambs
    ## Number of Threads
    ne.set_num_threads(nthreads)
    ## Constants for evaluation
    # Calculate these ones instead of few times!
    hold1  = ne.evaluate('sin(phif)' )
    hold2  = ne.evaluate('sin(phis)' )
    hold3  = ne.evaluate('cos(phif)' )
    hold4  = ne.evaluate('cos(dlamb)')
    hold5  = ne.evaluate('cos(phis)' )
    numera = ne.evaluate('hold3 * sin(dlamb)')
    numerb = ne.evaluate('hold5 * hold1 - hold2 * hold3 * hold4')
    numer  = ne.evaluate('sqrt(numera**2 + numerb**2)')
    denom  = ne.evaluate('hold2 * hold1 + hold5 * hold3 * hold4')
    pi     = math.pi
    # Great Circle Distance
    great_circle_dist = ne.evaluate('(arctan2(numer, denom))*180.0/pi')

    return great_circle_dist

## Sphere Match
def spherematch(ra1, dec1, ra2, dec2, tol=None, nnearest=1, nthreads=1):
    """
    Determines the matches between two catalogues of sources with
    <ra, dec> coordinates.

    Parameters
    ----------
    ra1, dec1 : array_like
        Right ascension and declination of the 1st catalogue.
        Units are in `degrees`.

    ra2, dec2 : array_like
        Right ascension and declination of the 2nd catalogue.
        Units are in `degrees`.

    tol : float or None, optional
        How close (in degrees) a match has to be to count as a match.
        If None, all nearest neighbors for the 1st catalogue will be returned.

    nnearest : int, optional
        The nth neighbor to find. E.g. 1 for the nearest nearby, 2 for the
        second nearest neighbor, etc. Partcularly useful if you want to get
        the nearest *non-self* neighbor of a catalogue.
        To do this use::

        ``spherematch(ra, dec, ra, dec, nnearest=2)``

        if `nnearest == 0`, all matches are returned.

    nthreads : int, optional
        Number of threads to use for calculation. This variable is set to
        1 by default. Must be larger than 1.

    Returns
    ----------
    idx1 : int `numpy.ndarray`
        Indices of the 1st catalogue of the matches. Will never be larger
        than `ra1`/`dec1`.

    idx2 : int `numpy.ndarray`
        Indices of the 2nd catalogue of the matches. Will never be larger
        than `ra1`/`dec1`.

    ds : float `numpy.ndarray`
        Distance (in degrees) between the matches.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input arguments
    valid_types = (list, np.ndarray)
    # `ra1`
    if not (isinstance(ra1, valid_types)):
        msg = '{0} `ra1` ({1}) is not a valid type!'.format(
            file_msg, type(ra1))
        raise LSSUtils_Error(msg)
    # `dec1`
    if not (isinstance(dec1, valid_types)):
        msg = '{0} `dec1` ({1}) is not a valid type!'.format(
            file_msg, type(dec1))
        raise LSSUtils_Error(msg)
    # `ra2`
    if not (isinstance(ra2, valid_types)):
        msg = '{0} `ra2` ({1}) is not a valid type!'.format(
            file_msg, type(ra2))
        raise LSSUtils_Error(msg)
    # `dec2`
    if not (isinstance(dec2, valid_types)):
        msg = '{0} `dec2` ({1}) is not a valid type!'.format(
            file_msg, type(dec2))
        raise LSSUtils_Error(msg)
    # `nnearest`
    if nnearest < 0:
        msg = '{0} `nnearest` ({1}) must be larger than `0`!'.format(
            file_msg,
            nnearest)
        raise LSSUtils_Error(msg)
    # `threads`
    if nthreads < 1:
        msg = '{0} `nthreads` ({1}) must be larger than `1`!'.format(
            file_msg,
            nthreads)
        raise LSSUtils_Error(msg)
    ##
    ## Converting arguments into arrays for ease of use
    ra1  = np.array(ra1 , copy=False)
    dec1 = np.array(dec1, copy=False)
    ra2  = np.array(ra2 , copy=False)
    dec2 = np.array(dec2, copy=False)
    ## Checking shape
    # 1st catalogue
    if ra1.shape != dec1.shape:
        msg = '{0} The shape of `ra1` ({1}) does not mathc that of `dec1` ({2}).'
        msg = msg.format(file_msg, ra1.shape, dec1.shape)
        raise LSSUtils_Error(msg)
    # 2nd catalogue
    if ra2.shape != dec2.shape:
        msg = '{0} The shape of `ra2` ({1}) does not mathc that of `dec2` ({2}).'
        msg = msg.format(file_msg, ra2.shape, dec2.shape)
        raise LSSUtils_Error(msg)
    ##
    ## Converting spherical coordinates into cartesian coordinates
    # 1st catalogue
    x1, y1, z1 = _spherical_to_cartesian_fast(  ra1.ravel(),
                                                dec1.ravel(),
                                                nthreads)
    coords1 = np.empty((x1.size,3))
    coords1[:, 0] = x1
    coords1[:, 1] = y1
    coords1[:, 2] = z1
    # 2nd catalogue
    x2, y2, z2 = _spherical_to_cartesian_fast(  ra2.ravel(),
                                                dec2.ravel(),
                                                nthreads)
    coords2 = np.empty((x2.size,3))
    coords2[:, 0] = x2
    coords2[:, 1] = y2
    coords2[:, 2] = z2
    ##
    ## Finding nearest neighbors
    kdt = KDT(coords2)
    # Finding neighbors
    if nnearest == 1:
        idx_s2 = kdt.query(coords1)[1]
    elif (nnearest == 0) and (tol is not None): # if you want ALL matches!
        p1_x, p1_y, p1_z = _spherical_to_cartesian_fast(90., 0  , nthreads)
        p2_x, p2_y, p2_z = _spherical_to_cartesian_fast(90., tol, nthreads)
        # Converting to floats
        p1_x   = float(p1_x)
        p1_y   = float(p1_y)
        p1_z   = float(p1_z)
        p2_x   = float(p2_x)
        p2_y   = float(p2_y)
        p2_z   = float(p2_z)
        r      = np.sqrt((p2_x - p1_x)**2 + (p2_y - p1_y)**2 + (p2_z - p1_z)**2)
        idx_s2 = kdt.query_ball_point(coords1, r)[0]
    elif nnearest > 1:
        idx_s2 = kdt.query(coords1, nnearest)[1][:, -1]
    else:
        msg = '{0} Invalid `nnearest` ({1})!'.format(file_msg, nnearest)
        raise LSSUtils_Error(msg)
    ##
    ## Calculating distance between matches
    ds = _great_circle_distance_fast(   ra1         ,
                                        dec1        ,
                                        ra2[idx_s2] ,
                                        dec2[idx_s2],
                                        nthreads    )
    ##
    ## If `tol` is None, then all objects will have a match.
    idx_s1 = np.arange(ra1.size)
    ##
    ## Remove matches that are `beyond` the tolerance separation
    if (tol is not None) and (nnearest != 0):
        mask   = ds < tol
        idx_s1 = idx_s1[mask]
        idx_s2 = idx_s2[mask]
        ds     = ds    [mask]

    return idx_s1, idx_s2, ds
