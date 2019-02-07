#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-14
# Last Modified: 2018-05-14
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "Behroozi_relation"]

## Import modules
import numpy as np
from   cosmo_utils.utils             import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Retrieves default values for Behroozie et al. (2013)
def _retrieve_Behroozi_default_dict():
    """
    Dictionary of default values of all model parameters set to the
    column 2 values in Table 2 of Behroozi et al. (2013)

    Returns
    --------
    d : `dict`
        Dictionary containing default parameters for the Stellar-Halo
        Mass relation of Behroozi et al. (2013)

    Notes
    ----------
    All calculations are done internally ising the same h=0.7 units as
    in Behroozi ete al. (2010), ['arXiv:1001.0015'] so the parameter values
    here are the same as in Table 2, even though the `mean_log_halo_mass`
    and `mean_stellar_mass` methods use accept and return arguments in
    h=1 units.
    """
    ## Main dictionary
    d = ({'smhm_m0_0': 10.72,
        'smhm_m0_a': 0.59,
        'smhm_m1_0': 12.35,
        'smhm_m1_a': 0.3,
        'smhm_beta_0': 0.43,
        'smhm_beta_a': 0.18,
        'smhm_delta_0': 0.56,
        'smhm_delta_a': 0.18,
        'smhm_gamma_0': 1.54,
        'smhm_gamma_a': 2.52})

    return d

## Behroozi SHMR function
def Behroozi_relation(log_mstar, z=0.):
    """
    Returns the halo mass of a central galaxy as a function of its stellar
    mass.

    Parameters
    -----------
    log_mstar : `float` ,`np.ndarray`, or array-like
        Value or array of values of base-10 logarithm of stellar mass
        in h=1 solar mass units.

    z : int, float, `np.ndarray` or array-like
        Redshift of the halo hosting the galaxy. If passing an array,
        it must be of the same length as the input `log_mstar`.

    Returns
    -----------
    log_halo_mass : float or `np.ndarray`
        Array or float containing 10-base logarithm of halo mass in ``h=1``
        solar mass units.

    Notes
    ----------
    The parameter values in Behroozi+10 were fit to data assuming ``h=0.7``.
    Thus, we will transform our input stellar mass to ``h=0.7`` units,
    evaluate using the Behroozi parameters, and then transform back to
    ``h=1`` units before returning the result.
    """
    file_msg = fd.Program_Msg(__file__)
    little_h = 0.7
    ## Checking input parameters
    # `log_mstar`
    mstar_valid_types = (int, float, np.ndarray, list)
    if not (isinstance(log_mstar, mstar_valid_types)):
        msg = '{0} `log_mstar` ({1}) is not a valid type!'.format(
            file_msg, type(log_mstar))
        raise LSSUtils_Error(msg)
    # `z`
    z_valid_types = (int, float, np.ndarray, list)
    if not (isinstance(z, z_valid_types)):
        msg = '{0} `z` ({1}) is not a valid type!'.format(
            file_msg, type(z))
        raise LSSUtils_Error(msg)
    ##
    ## Behroozi dictionary
    param_dict = _retrieve_Behroozi_default_dict()
    ## COnverting stellar mass from ``h=1`` units to ``h=0.7`` units.
    mstar = (10.**log_mstar) / (little_h**2)
    ## Scale factor
    a = 1./(1. + z)
    ##
    ## Behroozi function
    logm0 = param_dict['smhm_m0_0'] + param_dict['smhm_m0_a']*(a - 1.)
    m0    = 10.**logm0
    logm1 = param_dict['smhm_m1_0'   ] + param_dict['smhm_m1_a'   ]*(a - 1)
    beta  = param_dict['smhm_beta_0' ] + param_dict['smhm_beta_a' ]*(a - 1)
    delta = param_dict['smhm_delta_0'] + param_dict['smhm_delta_a']*(a - 1)
    gamma = param_dict['smhm_gamma_0'] + param_dict['smhm_gamma_a']*(a - 1)
    #
    stellar_mass_by_m0 = mstar/m0
    term3_numerator    = (stellar_mass_by_m0)**delta
    term3_denominator  = 1. + (stellar_mass_by_m0)**(-gamma)
    #
    log_halo_mass = logm1 + beta*np.log10(stellar_mass_by_m0)
    log_halo_mass += (term3_numerator/term3_denominator) - 0.5
    #
    # Convert back from ``h=0.7`` to ``h=1`` units
    return np.log10((10.**log_halo_mass)*(little_h))
