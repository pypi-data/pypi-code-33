#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-10-03
# Last Modified: 2018-10-03
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "HOD"]

## Import modules
import numpy as np
import pandas as pd
import warnings
from   scipy                         import special, stats
from   cosmo_utils.utils             import stats_funcs
from   cosmo_utils.utils             import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions and classes

## Calculations of HOD parametrs

class HOD(object):
    """
    Computes various statistics corresponding to a given set of HOD parameters.
    HOD stands for `Halo Occupation Distribution`
    [http://arxiv.org/abs/astro-ph/0109001].
    """
    def __init__(self, **kwargs):
        """
        Parameters
        -----------
        use_identity : `bool`, optional
            If True, it uses the identity of expectation values, i.e.
            ``<A> + <B> = <A + B>``. If False, it returns the number of
            galaxies by computing the total number of central and
            satellite galaxies. This variable is set to 'True' by default.

        log_m0 : `float`
            Halo mass, below which there are no satellite galaxies.
        
        log_m1 : `float`
            Mass scale where haloes contain one satellite galaxy on average.

        log_Mmin : `float`
            Minimum halo mass that can host a `central` galaxy.

        sigma_logM : `float`
            Scatter around `Mmin`

        alpha : `float`
            Slope of the power-law occupation function at high masses.

        mass_bin : `float`, optional
            Bin/step size of the logarithmic halo mass array. This variable
            is set to ``0.01`` by default.

        log_mhalo_min : `float`, optional
            Minimum logarithmic halo mass to consider. This variable is set
            to ``10.`` by default.

        log_mhalo_max : `float`, optional
            Maximum logarithmic halo mass to consider. This variable is set
            to ``15.`` by default.
        """
        super().__init__()
        # Assigning variables
        self.use_identity         = kwargs.get('use_identity', True)
        self.log_m0               = kwargs.get('log_m0', 12.25)
        self.log_m1               = kwargs.get('log_m1', 12.56)
        self.log_Mmin             = kwargs.get('log_Mmin',  11.36)
        self.sigma_logM           = kwargs.get('sigma_logM',  0.14)
        self.alpha                = kwargs.get('alpha',  0.90)
        self.m0                   = 10.**self.log_m0
        self.m1                   = 10.**self.log_m1
        self.Mmin                 = 10.**self.log_Mmin
        # Extra variables
        self.hod_params           = self._retrieve_hod_params_dict()
        self.mass_bin             = kwargs.get('mass_bin', 0.01)
        self.log_mhalo_min        = kwargs.get('log_mhalo_min', 10.)
        self.log_mhalo_max        = kwargs.get('log_mhalo_max', 15.)
        # Arrays
        self.log_mhalo_arr        = self._log_mhalo_arr_create()
        self.mhalo_arr            = 10.**self.log_mhalo_arr

    # Average number of central galaxies as function of halo mass.
    def ncen_avg(self):
        """
        Computes the average number of `central` galaxies  as function of
        halo mass.

        Returns
        -----------
        ncen_avg_arr : `numpy.ndarray`
            Array of average number of central galaxies as function of
            halo mass.
        """
        # Special error function component
        erf_component  = (self.log_mhalo_arr - self.log_Mmin)
        erf_component /= self.sigma_logM
        # Average number of centrals
        ncen_avg_arr = 0.5 * (1. + special.erf(erf_component))

        return ncen_avg_arr

    # Average number of satellite galaxies as function of halo mass.
    def nsat_avg(self):
        """
        Computes the average number of `central` galaxies  as function of
        halo mass.

        Returns
        -----------
        nsat_avg_arr : `numpy.ndarray`
            Array of average number of central galaxies as function of
            halo mass.
        """
        # Average number of central galaxies
        ncen_avg_arr = self.ncen_avg()
        # Satellite galaxies
        nsat_comp = np.array([np.power((xx - self.m0)/self.m1, self.alpha)
                        if (xx >= self.m0) else 0. for xx in self.mhalo_arr])
        nsat_avg_arr = ncen_avg_arr * nsat_comp
        # nsat_avg_arr[np.isnan(nsat_avg_arr)] = 0.

        return nsat_avg_arr

    # Average number of galaxies (centrals and satellites) as function of halo
    # mass.
    def ngals_avg(self, arr_len=10, bin_statval='left',
        return_pd_dict=True, use_identity=True):
        """
        Computes the average number of galaxies (centrals + satellites) as
        function of halo mass.

        Parameters
        -----------
        arr_len :   `init`, optional
            Minimum number of elements in each bin of `x`. This variable
            is set to `0` by default.

        return_pd_dict : `bool`
            If True, it returns a dictionary with `pd.DataFrames` for
            each of the statistics.

        Returns
        ---------
        ngal_choice : `numpy.ndarray`
            Array of total number of galaxies. This variable depends on the
            choice of `use_identity`.
        """
        # Average number of central galaxies
        ncen_avg_arr = self.ncen_avg()
        # Average number of satellite galaxies
        nsat_avg_arr = self.nsat_avg()
        # Total number of galaxies
        ncen_arr = np.array([int(1) if xx > 0 else 0 for xx in ncen_avg_arr])
        nsat_arr = np.array([np.random.poisson(nsat_avg_arr[ii])
                        if ((ncen_avg_arr[ii] != 0) and (nsat_avg_arr[ii] > 0))
                        else 0 for ii in range(len(ncen_arr))])
        ngal_arr = ncen_arr + nsat_arr
        # Average number of galaxies using identity for expectation values
        ngal_avg_arr = ncen_avg_arr + nsat_avg_arr

        if use_identity:
            ngal_choice = ngal_avg_arr
        else:
            ngal_choice = ngal_arr

        return ngal_choice

    def ngals_avg_pd_create(self):
        """
        Creates a DataFrame with the information of mass and the average
        numbers of 1) Centrals, 2) satellites, and 3) all galaxies.

        Returns
        --------
        gals_pd : `pandas.DataFrame`
            DataFrame containing info about the average numbers of different
            types of galaxies and their corresponding halo masses.
        """
        # Average number of central galaxies
        ncen_avg_arr = self.ncen_avg()
        # Average number of satellite galaxies
        nsat_avg_arr = self.nsat_avg()
        # Average number of all galaxies
        ngal_avg_arr = self.ngals_avg()
        # Converting to DataFrame
        gals_pd      = pd.DataFrame({   'ncen': ncen_avg_arr,
                                        'nsat': nsat_avg_arr,
                                        'ngal': ngal_avg_arr,
                                        'log_mhalo': self.log_mhalo_arr})

        return gals_pd

    def _log_mhalo_arr_create(self):
        """
        Creates an array of fictitious halo masses.

        Returns
        --------
        log_mhalo_arr : `numpy.ndarray`
            Array of fictitious logarithmic halo masses.
        """
        # Constants
        log_mhalo_arr = np.arange(  self.log_mhalo_min,
                                    self.log_mhalo_max,
                                    self.mass_bin)

        return log_mhalo_arr

    def _retrieve_hod_params_dict(self):
        """
        Produced a dictionary with the HOD parameters

        Returns
        --------
        hod_params : `dict`
            Dictionary containing the sets of HOD parameters.
        """
        # Define dictionary
        hod_params = {}
        hod_params['log_m0'    ] = self.log_m0
        hod_params['log_m1'    ] = self.log_m1
        hod_params['log_Mmin'  ] = self.log_Mmin
        hod_params['sigma_logM'] = self.sigma_logM
        hod_params['alpha'     ] = self.alpha
        hod_params['m0'        ] = 10**self.log_m0
        hod_params['m1'        ] = 10**self.log_m1
        hod_params['Mmin'      ] = 10**self.log_Mmin

        return hod_params
