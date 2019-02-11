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
__all__        = [  "apparent_to_absolute_magnitude",
                    "absolute_to_apparent_magnitude",
                    "get_sun_mag",
                    "absolute_magnitude_to_luminosity",
                    "luminosity_to_absolute_mag",
                    "absolute_magnitude_lim"]

## Importing modules
import numpy as np
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Apparent to Absolute magnitudes
def apparent_to_absolute_magnitude(app_mag, lum_dist, unit='mpc'):
    """
    Calculates the absolute magnitude based on luminosity and apparent
    magnitude.

    Parameters
    -----------
    app_mag : array_like
        Array of apparent magnitude(s)

    lum_dist : array_like
        Array of luminosity distnace to object. In units of `Mpc`.

    unit : {'pc', 'kpc', 'mpc'} str, optional
        Unit to use for `lum_dist`. This variable is set to `mpc` by
        default. When `pc`, the units are in parsecs, while `mpc` is for
        distances in mega-parsecs, etc.

    Returns
    -----------
    abs_mag : np.ndarray
        Array of absolute magnitudes. `abs_mag` is a float if
        `app_mag` is a float or int.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    valid_types = (float, np.ndarray, list, int)
    # Type for `app_mag`
    if not (isinstance(app_mag, valid_types)):
        msg = '{0} `app_mag` ({1}) is not a valid type!'.format(file_msg,
            type(app_mag))
        raise LSSUtils_Error(msg)
    # Type for `unit`
    unit_valid_arr = ['mpc', 'kpc', 'pc']
    if not (unit in unit_valid_arr):
        msg = '{0} `unit` ({1}) is not a valid input!'.format(file_msg, unit)
        raise LSSUtils_Error(msg)
    ## Converting to array-type
    # `app_mag` object
    if (isinstance(app_mag, float) or isinstance(app_mag, int)):
        app_mag = float(app_mag)
    if (isinstance(app_mag, list) or isinstance(app_mag, np.ndarray)):
        app_mag = np.asarray(app_mag)
    # `lum_dist` object
    if (isinstance(lum_dist, float) or isinstance(lum_dist, int)):
        lum_dist = float(lum_dist)
    if (isinstance(lum_dist, list) or isinstance(lum_dist, np.ndarray)):
        lum_dist = np.asarray(lum_dist)
    # Units - Conveting to Mpc
    # This follows the formula:
    #   app_mag - abs_mag = 5 * (np.log10(lum_dist) + a - 1)
    #       Where a = 0 when [d] = parsecs
    #       Where a = 3 when [d] = kiloparsecs
    #       Where a = 6 when [d] = megaparsecs
    if unit == 'pc':
        a = 0
    elif unit == 'kpc':
        a = 3
    elif unit == 'mpc':
        a = 6
    ##
    ## Calcualtions
    abs_mag = app_mag - 5 * (np.log10(lum_dist) - 1 + a)

    return abs_mag

## Absolute to Apparent magnitudes
def absolute_to_apparent_magnitude(abs_mag, lum_dist, unit='mpc'):
    """
    Calculates the apparent magnitude using the luminosity and absolute
    magnitude.

    Parameters
    -----------
    abs_mag : float, int, or array_like
        Array of absolute magnitude(s)

    lum_dist : array_like
        Array of luminosity distnace to object. In units of `Mpc`.

    unit : {'pc', 'kpc', 'mpc'} str, optional
        Unit to use for `lum_dist`. This variable is set to `mpc` by
        default. When `pc`, the units are in parsecs, while `mpc` is for
        distances in mega-parsecs, etc.

    Returns
    -----------
    app_mag : array_like, or float
        Array of apparent magnitude(s). `app_mag` is a float if
        `abs_mag` is a float or int.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    valid_types = (float, np.ndarray, list, int)
    # Type for `abs_mag`
    if not (isinstance(abs_mag, valid_types)):
        msg = '{0} `abs_mag` ({1}) is not a valid type!'.format(file_msg,
            type(abs_mag))
        raise LSSUtils_Error(msg)
    # Type for `unit`
    unit_valid_arr = ['mpc', 'pc']
    if not (unit in unit_valid_arr):
        msg = '{0} `unit` ({1}) is not a valid input!'.format(file_msg, unit)
        raise LSSUtils_Error(msg)
    ## Converting to array-type
    # `abs_mag` object
    if (isinstance(abs_mag, float) or isinstance(abs_mag, int)):
        abs_mag = float(abs_mag)
    if (isinstance(abs_mag, list) or isinstance(abs_mag, np.ndarray)):
        abs_mag = np.asarray(abs_mag)
    # `lum_dist` object
    if (isinstance(lum_dist, float) or isinstance(lum_dist, int)):
        lum_dist = float(lum_dist)
    if (isinstance(lum_dist, list) or isinstance(lum_dist, np.ndarray)):
        lum_dist = np.asarray(lum_dist)
    # Units - Conveting to Mpc
    # This follows the formula:
    #   app_mag - abs_mag = 5 * (np.log10(lum_dist) + a - 1)
    #       Where a = 0 when [d] = parsecs
    #       Where a = 3 when [d] = kiloparsecs
    #       Where a = 6 when [d] = megaparsecs
    if unit == 'pc':
        a = 0
    elif unit == 'kpc':
        a = 3
    elif unit == 'mpc':
        a = 6
    ##
    ## Calcualtions
    app_mag = abs_mag + 5. * (np.log10(lum_dist) - 1 + a)

    return app_mag

## Sun's magnitudes
def get_sun_mag(filter_opt, system='SDSS_Blanton_2003_z0.1'):
    """
    Get solar absolaute magnitude for a filter in a system.
    Taken from Duncan Campbell, and later modified.

    Parameters
    ----------
    filter_opt : {'U', 'B', 'V', 'R', 'I', 'J', 'H', 'K'} str
        Magnitude filter to use.

    system : {'Binney_and_Merrifield_1998', 'SDSS_Blanton_2003_z0.1'} str
        Kind of filter to use.

        Options:
            - 'Binney_and_Merrifield_1998' : See Binney and Merrifield, 1998
            - 'SDSS_Blanton_2003_z0.1' : See Blanton et al. (2003) Eqn. 14.

    Returns
    ----------
    abs_mag_sun : float
        Solar absolute magnitude in `filter_opt` using `system` parameters.

    Raises
    ----------
    LSSUtils_Error : Exception
        Program exception if input parameters are accepted

    Examples
    ----------
    >>> get_sun_mag('R', 'Binney_and_Merrifield_1998')
    4.42

    >>> get_sun_mag('V', 'Binney_and_Merrifield_1998')
    4.83

    >>> get_sun_mag('g', 'SDSS_Blanton_2003_z0.1')
    5.45
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    filter_arr = ['U', 'B', 'V', 'R', 'I', 'J', 'H', 'K', 'u','g','r','i','z']
    system_arr = ['Binney_and_Merrifield_1998', 'SDSS_Blanton_2003_z0.1']
    # Checks
    # Input filter
    if not (filter_opt in filter_arr):
        msg = '{0} `filter_opt` ({1}) is not a valid option!'.format(
            file_msg, filter_opt)
        raise LSSUtils_Error
    # Input system
    if not (system in system_arr):
        msg = '{0} `system` ({1}) is not a valid option!'.format(
            file_msg, system)
        raise LSSUtils_Error
    ##
    ## Input parameters
    abs_mag_sun_dict = {'Binney_and_Merrifield_1998' : {'U': 5.61,
                                                        'B': 5.48,
                                                        'V': 4.83,
                                                        'R': 4.42,
                                                        'I': 4.08,
                                                        'J': 3.64,
                                                        'H': 3.32,
                                                        'K': 3.28},
                        'SDSS_Blanton_2003_z0.1'    : { 'u': 6.80,
                                                        'g': 5.45,
                                                        'r': 4.76,
                                                        'i': 4.58,
                                                        'z': 4.51}}
    ## Checking if key exists in dictionary
    ## and assigning magnitude
    if (filter_opt in abs_mag_sun_dict[system].keys()):
        abs_mag_sun = abs_mag_sun_dict[system][filter_opt]
    else:
        msg = '{0} `filter_opt` ({1}) is not a proper key of `system` ({2})'
        msg = msg.format(file_msg, filter_opt, system)
        raise LSSUtils_Error(msg)

    return abs_mag_sun

## Absolute magnitude to luminosity
def absolute_magnitude_to_luminosity(abs_mag, filter_opt,
    system='SDSS_Blanton_2003_z0.1'):
    """
    Calculates the luminosity of the object through `filter_opt` filter.

    Parameters
    -----------
    abs_mag : float, int, or array_like
        Absolute magnitude of one or multiple objects.

    filter_opt : {'U', 'B', 'V', 'R', 'I', 'J', 'H', 'K'} str
        Magnitude filter to use.

    system : {'Binney_and_Merrifield_1998', 'SDSS_Blanton_2003_z0.1'} str
        Kind of filter to use.

        Options:
            - 'Binney_and_Merrifield_1998' : See Binney and Merrifield, 1998
            - 'SDSS_Blanton_2003_z0.1' : See Blanton et al. (2003) Eqn. 14.

    Returns
    -----------
    log_L : float or array_like
        Logarithmic value of the luminosity in the `filter_opt` band.

    Raises
    ----------
    LSSUtils_Error : Exception
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    valid_types = (float, int, list, np.ndarray)
    if not (isinstance(abs_mag, valid_types)):
        msg = '{0} `abs_mag` ({1}) is not a valid type!'.format(file_msg,
            abs_mag)
        raise LSSUtils_Error(msg)
    ## Obtaining Sun's absolute magnitude
    abs_mag_sun = get_sun_mag(filter_opt, system=system)
    ## Luminosity calculations
    log_L = (abs_mag_sun - abs_mag) * 0.4

    return log_L

## Luminosity to Absolute magnitude
def luminosity_to_absolute_mag(lum, filter_opt,
    system='SDSS_Blanton_2003_z0.1'):
    """
    Calculates the absolute magnitude of object through the `filter_opt`
    filter.

    Parameters
    -----------
    lum : float, int, array_like
        Luminosity of 1 or more objects. In units of `solar luminosities`.

    filter_opt : {'U', 'B', 'V', 'R', 'I', 'J', 'H', 'K'} str
        Magnitude filter to use.

    system : {'Binney_and_Merrifield_1998', 'SDSS_Blanton_2003_z0.1'} str
        Kind of filter to use.

        Options:
            - 'Binney_and_Merrifield_1998' : See Binney and Merrifield, 1998
            - 'SDSS_Blanton_2003_z0.1' : See Blanton et al. (2003) Eqn. 14.

    Returns
    -----------
    abs_mag : float, int, or array_like
        Absolute magnitude of one or multiple objects. Same type as `lum`

    Raises
    ----------
    LSSUtils_Error : Exception
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    valid_types = (float, int, list, np.ndarray)
    if not (isinstance(lum, valid_types)):
        msg = '{0} `lum` ({1}) is not a valid type!'.format(file_msg,
            lum)
        raise LSSUtils_Error(msg)
    ## Obtaining Sun's absolute magnitude
    abs_mag_sun = get_sun_mag(filter_opt, system=system)
    ## Absolute magnitude calculation
    # In units of solar luminosities
    lum_sun = 1.0
    # Absolute magnitude of objects
    abs_mag = abs_mag_sun - 2.5 * np.log10(lum / lum_sun)

    return abs_mag

## Absolute magnitude limits
def absolute_magnitude_lim(z, mag_lim, cosmo=None, H0=100., verbose=True):
    """
    Calculates the absolute magnitude limit as function of redshift `z` for
    a flux-limited survey.

    Parameters
    -----------
    z : float, int, or array_like
        Maximum redshift for a given flux-limited survey.

    mag_lim : float
        Apparent magnitude limit of the flux-limited survey.

    cosmo : `astropy.cosmology` object
        Cosmology object from Astropy.

    H0 : float, optional
        Hubble parameters value used to estimate distances.
        This variable is set to 100 km/s/Mpc by default.

    verbose : `bool`, optional
        If True, a message will appear when the default cosmology is used.

    Returns
    -----------
    abs_mag : float, int, or array_like
        Absolute magnitude limit in units of `abs_mag` + 5*log10(h),
        where `h` is the little Hubble parameter.

    Raises
    ----------
    LSSUtils_Error : Exception
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    # Redshift
    z_valid_types = (float, int, list, np.ndarray)
    if not (isinstance(z, z_valid_types)):
        msg = '{0} `z` ({1}) is not a valid type!'.format(file_msg, type(z))
        raise LSSUtils_Error(msg)
    # Magnitude limit
    mag_lim_valid_types = (float, int)
    if not (isinstance(mag_lim, mag_lim_valid_types)):
        msg = '{0} `mag_lim` ({1}) is not a valid type!'.format(file_msg,
            type(mag_lim))
        raise LSSUtils_Error(msg)
    # Hubble parameter value
    H0_valid_types = (float, int)
    if not (isinstance(H0, H0_valid_types)):
        msg = '{0} `H0` ({1}) is not a valid type!'.format(file_msg,
            type(H0))
        raise LSSUtils_Error(msg)
    ##
    ## Calculations
    if not cosmo:
        from astropy.cosmology import FlatLambdaCDM
        cosmo = FlatLambdaCDM(H0=H0, Om0=0.316)
        if verbose:
            print(">> Warning: No cosmology was specified. Using default:",
                cosmo)
    ## Luminosity distance
    lum_dist = cosmo.luminosity_distance(z).value
    ## Absolute magnitude
    abs_mag = apparent_to_absolute_magnitude(mag_lim, lum_dist)

    return abs_mag
