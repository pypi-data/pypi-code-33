#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-12-24
# Last Modified: 2018-12-24
# Vanderbilt University
from __future__ import (absolute_import, division, print_function )
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon, 2018"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
"""
Set of test functions for the `download_manager` functions
"""

import numpy as np
import pytest
from sdss_catl_utils.models.catl_models import DownloadManager
from sdss_catl_utils.custom_exceptions import SDSSCatlUtils_Error

## Functions

#########-------------------------------------------------------------#########
#########-------------------------------------------------------------#########

#### ------------------- Test `DownloadManager` function - Types ----------- ##

catl_kind_arr    = ['data', 'mocks']
hod_n_arr        = [1,2]
halotype_arr     = ['so', 'fof']
clf_method_arr   = [1, 2, 3]
clf_seed_arr     = [1, 4]
dv_arr           = np.arange(0.5, 2.0, 1.)
sample_arr       = ['19', '20', '21']
type_am_arr      = ['mr', 'mstar']
cosmo_choice_arr = ['Planck', 'LasDamas']
perf_opt_arr     = [True, False]
remove_files_arr = [True, False]
environ_name_arr = ['Env1']
sigma_clf_c_arr  = [0.1, 0.2, 0.3]

@pytest.mark.parametrize('catl_kind', catl_kind_arr)
@pytest.mark.parametrize('hod_n', hod_n_arr)
@pytest.mark.parametrize('halotype', halotype_arr)
@pytest.mark.parametrize('clf_method', clf_method_arr)
@pytest.mark.parametrize('clf_seed', clf_seed_arr)
@pytest.mark.parametrize('dv', dv_arr)
@pytest.mark.parametrize('sigma_clf_c', sigma_clf_c_arr)
@pytest.mark.parametrize('sample', sample_arr)
@pytest.mark.parametrize('type_am', type_am_arr)
@pytest.mark.parametrize('cosmo_choice', cosmo_choice_arr)
@pytest.mark.parametrize('perf_opt', perf_opt_arr)
@pytest.mark.parametrize('remove_files', remove_files_arr)
@pytest.mark.parametrize('environ_name', environ_name_arr)
def test_DownloadManager_inputs_types(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name, sigma_clf_c):
    """
    Checks the function `~sdss_catl_utils.mocks_manager.download_manager.DownloadManager`
    for input parameters.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`
        Kind of catalogues to download. This variable is set to
        ``mocks`` by default.

        Options:
            - ``data``: Downloads the SDSS DR7 real catalogues.
            - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

    hod_n : `int`, optional
        Number of the HOD model to use. This value is set to `0` by
        default.

    halotype : {'so', 'fof'}, `str`, optional
        Type of dark matter definition to use. This value is set to
        ``so`` by default.

        Options:
            - ``so``: Spherical Overdensity halo definition.
            - ``fof``: Friends-of-Friends halo definition.

    clf_method : {1, 2, 3}, `int`, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable dictates how galaxies are assigned
        luminosities or stellar masses based on their galaxy type
        and host halo's mass. This variable is set to ``1`` by
        default.

        Options:
            - ``1``: Independent assignment of (g-r) colour, sersic, and specific star formation rate (`logssfr`)
            - ``2``: (g-r) colour dictates active/passive designation and draws values independently.
            - ``3``: (g-r) colour dictates active/passive designation, and assigns other galaxy properties for that given galaxy.

    clf_seed : `int`, optional
        Value of the random seed used for the conditional luminosity function.
        This variable is set to ``1235`` default.

    dv : `float`, optional
        Value for the ``velocity bias`` parameter. It is the difference
        between the galaxy and matter velocity profiles.

        .. math::
            dv = \\frac{v_{g} - v_{c}}{v_{m} - v_{c}}

        where :math:`v_g` is the galaxy's velocity; :math:`v_m`, the
        matter velocity.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies, when being
        assigned during the `conditional luminosity function` (CLF).
        This variable is set to ``0.1417`` by default.

    sample : {'19', '20', '21'}, `str`, optional
        Luminosity of the SDSS volume-limited sample to analyze.
        This variable is set to ``'19'`` by default.

        Options:
            - ``'19'``: :math:`M_r = 19` volume-limited sample
            - ``'20'``: :math:`M_r = 20` volume-limited sample
            - ``'21'``: :math:`M_r = 21` volume-limited sample

    catl_type : {'mr', 'mstar'}, `str`, optional
        Type of Abundance matching used in the catalogue. This
        variable is set to ``'mr'`` by default.

        Options:
            - ``'mr'``: Luminosity-based abundance matching used
            - ``'mstar'``: Stellar-mass-based abundance matching used.

    cosmo_choice : { ``'LasDamas'``, ``'Planck'``} `str`, optional
        Choice of cosmology to use. This variable is set to ``LasDamas``
        by default.

        Options:
            - ``LasDamas`` : Uses the cosmological parameters from the 
                `LasDamas <http://lss.phy.vanderbilt.edu/lasdamas/simulations.html>`_ simulations.
            - ``Planck`` : Uses the Planck 2015 cosmology.

    perf_opt : `bool`, optional
        If `True`, it chooses to analyze the ``perfect`` version of
        the synthetic galaxy/group galaxy catalogues. Otherwise,
        it downloads the catalogues with group-finding errors
        included. This variable is set to ``False`` by default.

    environ_name : `str`
        Name of the environment variable to assign to ``outdir``.
        This variable is set to the default ``environ_name`` from
        `~sdss_catl_utils.mocks_manager.mocks_default`
    """
    # Creating dictionary
    input_dict = {  'catl_kind': catl_kind,
                    'hod_n': hod_n,
                    'halotype': halotype,
                    'clf_method': clf_method,
                    'clf_seed': clf_seed,
                    'dv': dv,
                    'sigma_clf_c': sigma_clf_c,
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    obj_ii = DownloadManager(**input_dict)

#### ------------- Test `DownloadManager` function - Error - Types --------------- ##

input_arr_type = [\
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 1, 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, 'str', 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', 'str', True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 123, True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 1000, 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, 1, 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 'test', '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, '1', 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', '1', 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 10, 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', '2', 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        (32, 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 'sig')]
input_str_type  = 'catl_kind, hod_n, halotype, clf_method, clf_seed, dv, sample, '
input_str_type += 'type_am, cosmo_choice, perf_opt, remove_files, environ_name, '
input_str_type += 'sigma_clf_c'
@pytest.mark.parametrize(input_str_type, input_arr_type)
def test_DownloadManager_inputs_err_type(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name, sigma_clf_c):
    """
    Checks the function `~sdss_catl_utils.mocks_manager.download_manager.DownloadManager`
    for input parameters.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`
        Kind of catalogues to download. This variable is set to
        ``mocks`` by default.

        Options:
            - ``data``: Downloads the SDSS DR7 real catalogues.
            - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

    hod_n : `int`, optional
        Number of the HOD model to use. This value is set to `0` by
        default.

    halotype : {'so', 'fof'}, `str`, optional
        Type of dark matter definition to use. This value is set to
        ``so`` by default.

        Options:
            - ``so``: Spherical Overdensity halo definition.
            - ``fof``: Friends-of-Friends halo definition.

    clf_method : {1, 2, 3}, `int`, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable dictates how galaxies are assigned
        luminosities or stellar masses based on their galaxy type
        and host halo's mass. This variable is set to ``1`` by
        default.

        Options:
            - ``1``: Independent assignment of (g-r) colour, sersic, and specific star formation rate (`logssfr`)
            - ``2``: (g-r) colour dictates active/passive designation and draws values independently.
            - ``3``: (g-r) colour dictates active/passive designation, and assigns other galaxy properties for that given galaxy.

    clf_seed : `int`, optional
        Value of the random seed used for the conditional luminosity function.
        This variable is set to ``1235`` default.

    dv : `float`, optional
        Value for the ``velocity bias`` parameter. It is the difference
        between the galaxy and matter velocity profiles.

        .. math::
            dv = \\frac{v_{g} - v_{c}}{v_{m} - v_{c}}

        where :math:`v_g` is the galaxy's velocity; :math:`v_m`, the
        matter velocity.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies, when being
        assigned during the `conditional luminosity function` (CLF).
        This variable is set to ``0.1417`` by default.

    sample : {'19', '20', '21'}, `str`, optional
        Luminosity of the SDSS volume-limited sample to analyze.
        This variable is set to ``'19'`` by default.

        Options:
            - ``'19'``: :math:`M_r = 19` volume-limited sample
            - ``'20'``: :math:`M_r = 20` volume-limited sample
            - ``'21'``: :math:`M_r = 21` volume-limited sample

    catl_type : {'mr', 'mstar'}, `str`, optional
        Type of Abundance matching used in the catalogue. This
        variable is set to ``'mr'`` by default.

        Options:
            - ``'mr'``: Luminosity-based abundance matching used
            - ``'mstar'``: Stellar-mass-based abundance matching used.

    cosmo_choice : { ``'LasDamas'``, ``'Planck'``} `str`, optional
        Choice of cosmology to use. This variable is set to ``LasDamas``
        by default.

        Options:
            - ``LasDamas`` : Uses the cosmological parameters from the 
                `LasDamas <http://lss.phy.vanderbilt.edu/lasdamas/simulations.html>`_ simulations.
            - ``Planck`` : Uses the Planck 2015 cosmology.

    perf_opt : `bool`, optional
        If `True`, it chooses to analyze the ``perfect`` version of
        the synthetic galaxy/group galaxy catalogues. Otherwise,
        it downloads the catalogues with group-finding errors
        included. This variable is set to ``False`` by default.

    environ_name : `str`
        Name of the environment variable to assign to ``outdir``.
        This variable is set to the default ``environ_name`` from
        `~sdss_catl_utils.mocks_manager.mocks_default`
    """
    # Creating dictionary
    input_dict = {  'catl_kind': catl_kind,
                    'hod_n': hod_n,
                    'halotype': halotype,
                    'clf_method': clf_method,
                    'clf_seed': clf_seed,
                    'dv': dv,
                    'sigma_clf_c': sigma_clf_c,
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    with pytest.raises(TypeError):
        obj_ii = DownloadManager(**input_dict)

#### ------------- Test `DownloadManager` function - Error - Values --------------- ##

input_arr_vals = [\
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'LasDamas1', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck1', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr2', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mstar2', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, '191', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 1, 1, 0.6, 'a', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 0, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 5, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so', 4, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'so1', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 1, 'fof2', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 12, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data', 98, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('data_1', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1),
        ('mocks2', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a', 0.1)]
input_str_vals  = 'catl_kind, hod_n, halotype, clf_method, clf_seed, dv, sample, '
input_str_vals += 'type_am, cosmo_choice, perf_opt, remove_files, environ_name, '
input_str_vals += 'sigma_clf_c'
@pytest.mark.parametrize(input_str_vals, input_arr_vals)
def test_DownloadManager_inputs_err_vals(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name, sigma_clf_c):
    """
    Checks the function `~sdss_catl_utils.mocks_manager.download_manager.DownloadManager`
    for input parameters.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`
        Kind of catalogues to download. This variable is set to
        ``mocks`` by default.

        Options:
            - ``data``: Downloads the SDSS DR7 real catalogues.
            - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

    hod_n : `int`, optional
        Number of the HOD model to use. This value is set to `0` by
        default.

    halotype : {'so', 'fof'}, `str`, optional
        Type of dark matter definition to use. This value is set to
        ``so`` by default.

        Options:
            - ``so``: Spherical Overdensity halo definition.
            - ``fof``: Friends-of-Friends halo definition.

    clf_method : {1, 2, 3}, `int`, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable dictates how galaxies are assigned
        luminosities or stellar masses based on their galaxy type
        and host halo's mass. This variable is set to ``1`` by
        default.

        Options:
            - ``1``: Independent assignment of (g-r) colour, sersic, and specific star formation rate (`logssfr`)
            - ``2``: (g-r) colour dictates active/passive designation and draws values independently.
            - ``3``: (g-r) colour dictates active/passive designation, and assigns other galaxy properties for that given galaxy.

    clf_seed : `int`, optional
        Value of the random seed used for the conditional luminosity function.
        This variable is set to ``1235`` default.

    dv : `float`, optional
        Value for the ``velocity bias`` parameter. It is the difference
        between the galaxy and matter velocity profiles.

        .. math::
            dv = \\frac{v_{g} - v_{c}}{v_{m} - v_{c}}

        where :math:`v_g` is the galaxy's velocity; :math:`v_m`, the
        matter velocity.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies, when being
        assigned during the `conditional luminosity function` (CLF).
        This variable is set to ``0.1417`` by default.

    sample : {'19', '20', '21'}, `str`, optional
        Luminosity of the SDSS volume-limited sample to analyze.
        This variable is set to ``'19'`` by default.

        Options:
            - ``'19'``: :math:`M_r = 19` volume-limited sample
            - ``'20'``: :math:`M_r = 20` volume-limited sample
            - ``'21'``: :math:`M_r = 21` volume-limited sample

    catl_type : {'mr', 'mstar'}, `str`, optional
        Type of Abundance matching used in the catalogue. This
        variable is set to ``'mr'`` by default.

        Options:
            - ``'mr'``: Luminosity-based abundance matching used
            - ``'mstar'``: Stellar-mass-based abundance matching used.

    cosmo_choice : { ``'LasDamas'``, ``'Planck'``} `str`, optional
        Choice of cosmology to use. This variable is set to ``LasDamas``
        by default.

        Options:
            - ``LasDamas`` : Uses the cosmological parameters from the 
                `LasDamas <http://lss.phy.vanderbilt.edu/lasdamas/simulations.html>`_ simulations.
            - ``Planck`` : Uses the Planck 2015 cosmology.

    perf_opt : `bool`, optional
        If `True`, it chooses to analyze the ``perfect`` version of
        the synthetic galaxy/group galaxy catalogues. Otherwise,
        it downloads the catalogues with group-finding errors
        included. This variable is set to ``False`` by default.

    environ_name : `str`
        Name of the environment variable to assign to ``outdir``.
        This variable is set to the default ``environ_name`` from
        `~sdss_catl_utils.mocks_manager.mocks_default`
    """
    # Creating dictionary
    input_dict = {  'catl_kind': catl_kind,
                    'hod_n': hod_n,
                    'halotype': halotype,
                    'clf_method': clf_method,
                    'clf_seed': clf_seed,
                    'dv': dv,
                    'sigma_clf_c': sigma_clf_c,
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    with pytest.raises(ValueError):
        obj_ii = DownloadManager(**input_dict)

#### ------------ Test `DownloadManager` function - _catl_prefix ----------- ##
prefix_arr = [\
    ('data', 0, 'fof', 1, 12, 0.1417, 1.0, '19', 'mr', False, 'memb', 'data/mr/Mr19/member_galaxy_catalogues'),
    ('data', 0, 'fof', 1, 12, 0.1, 1.0, '20', 'mr', False, 'memb', 'data/mr/Mr20/member_galaxy_catalogues'),
    ('data', 0, 'fof', 1, 12, 0.1, 1.0, '21', 'mr', False, 'memb', 'data/mr/Mr21/member_galaxy_catalogues'),
    ('mocks', 0, 'fof', 1, 12, 0.25, 1.0, '19', 'mr', False, 'memb', 'mocks/halos_fof/dv_1.0/hod_model_0/clf_seed_12/clf_method_1/sigma_c_0.25/mr/Mr19/member_galaxy_catalogues'),
    ('mocks', 0, 'so', 1, 12, 0.1, 1.0, '19', 'mr', False, 'memb', 'mocks/halos_so/dv_1.0/hod_model_0/clf_seed_12/clf_method_1/sigma_c_0.1/mr/Mr19/member_galaxy_catalogues'),
    ('mocks', 0, 'so', 1, 12, 0.1, 1.0, '19', 'mr', True, 'memb', 'mocks/halos_so/dv_1.0/hod_model_0/clf_seed_12/clf_method_1/sigma_c_0.1/mr/Mr19/perfect_member_galaxy_catalogues'),
    ('mocks', 0, 'so', 1, 400, 0.1, 1.0, '19', 'mr', True, 'memb', 'mocks/halos_so/dv_1.0/hod_model_0/clf_seed_400/clf_method_1/sigma_c_0.1/mr/Mr19/perfect_member_galaxy_catalogues'),
    ('mocks', 0, 'so', 1, 400, 0.1, 1.0, '19', 'mr', False, 'group', 'mocks/halos_so/dv_1.0/hod_model_0/clf_seed_400/clf_method_1/sigma_c_0.1/mr/Mr19/group_galaxy_catalogues'),
    ('mocks', 1, 'so', 1, 400, 0.1, 1.05, '21', 'mstar', False, 'group', 'mocks/halos_so/dv_1.05/hod_model_1/clf_seed_400/clf_method_1/sigma_c_0.1/mstar/Mr21/group_galaxy_catalogues'),
    ('mocks', 1, 'so', 1, 400, 0.1, 1.05, '21', 'mstar', False, 'gal', 'mocks/halos_so/dv_1.05/hod_model_1/clf_seed_400/clf_method_1/sigma_c_0.1/mstar/Mr21/galaxy_catalogues'),
    ('mocks', 1, 'so', 1, 400, 0.1, 1.05, '21', 'mstar', True, 'gal', 'mocks/halos_so/dv_1.05/hod_model_1/clf_seed_400/clf_method_1/sigma_c_0.1/mstar/Mr21/galaxy_catalogues'),
    ('mocks', 1, 'so', 1, 400, 0.1, 1.05, '21', 'mstar', True, 'group', 'mocks/halos_so/dv_1.05/hod_model_1/clf_seed_400/clf_method_1/sigma_c_0.1/mstar/Mr21/perfect_group_galaxy_catalogues'),
    ('mocks', 1, 'so', 1, 400, 0.1, 1.25, '20', 'mstar', True, 'memb', 'mocks/halos_so/dv_1.25/hod_model_1/clf_seed_400/clf_method_1/sigma_c_0.1/mstar/Mr20/perfect_member_galaxy_catalogues')
    ]
prefix_str  = 'catl_kind, hod_n, halotype, clf_method, clf_seed, sigma_clf_c,'
prefix_str += 'dv, sample, type_am, perf_opt, catl_type, expected' 
@pytest.mark.parametrize(prefix_str, prefix_arr)
def test_DownloadManager_catl_prefix(catl_kind, hod_n, halotype, clf_method,
    clf_seed, sigma_clf_c, dv, sample, type_am, perf_opt, catl_type, expected):
    """
    Checks the function `~sdss_catl_utils.mocks_manager.download_manager.DownloadManager`
    for catalogue prefix strings.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`
        Kind of catalogues to download. This variable is set to
        ``mocks`` by default.

        Options:
            - ``data``: Downloads the SDSS DR7 real catalogues.
            - ``mocks``: Downloads the synthetic catalogues of SDSS DR7.

    hod_n : `int`, optional
        Number of the HOD model to use. This value is set to `0` by
        default.

    halotype : {'so', 'fof'}, `str`, optional
        Type of dark matter definition to use. This value is set to
        ``so`` by default.

        Options:
            - ``so``: Spherical Overdensity halo definition.
            - ``fof``: Friends-of-Friends halo definition.

    clf_method : {1, 2, 3}, `int`, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable dictates how galaxies are assigned
        luminosities or stellar masses based on their galaxy type
        and host halo's mass. This variable is set to ``1`` by
        default.

        Options:
            - ``1``: Independent assignment of (g-r) colour, sersic, and specific star formation rate (`logssfr`)
            - ``2``: (g-r) colour dictates active/passive designation and draws values independently.
            - ``3``: (g-r) colour dictates active/passive designation, and assigns other galaxy properties for that given galaxy.

    clf_seed : `int`, optional
        Value of the random seed used for the conditional luminosity function.
        This variable is set to ``1235`` default.

    dv : `float`, optional
        Value for the ``velocity bias`` parameter. It is the difference
        between the galaxy and matter velocity profiles.

        .. math::
            dv = \\frac{v_{g} - v_{c}}{v_{m} - v_{c}}

        where :math:`v_g` is the galaxy's velocity; :math:`v_m`, the
        matter velocity.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies, when being
        assigned during the `conditional luminosity function` (CLF).
        This variable is set to ``0.1417`` by default.

    sample : {'19', '20', '21'}, `str`, optional
        Luminosity of the SDSS volume-limited sample to analyze.
        This variable is set to ``'19'`` by default.

        Options:
            - ``'19'``: :math:`M_r = 19` volume-limited sample
            - ``'20'``: :math:`M_r = 20` volume-limited sample
            - ``'21'``: :math:`M_r = 21` volume-limited sample

    type_am : {'mr', 'mstar'}, `str`, optional
        Type of Abundance matching used in the catalogue. This
        variable is set to ``'mr'`` by default.

        Options:
            - ``'mr'``: Luminosity-based abundance matching used
            - ``'mstar'``: Stellar-mass-based abundance matching used.
    
    perf_opt : `bool`, optional
        If `True`, it chooses to analyze the ``perfect`` version of
        the synthetic galaxy/group galaxy catalogues. Otherwise,
        it downloads the catalogues with group-finding errors
        included. This variable is set to ``False`` by default.
    """
    # Creating dictionary
    input_dict = {  'catl_kind': catl_kind,
                    'hod_n': hod_n,
                    'halotype': halotype,
                    'clf_method': clf_method,
                    'clf_seed': clf_seed,
                    'dv': dv,
                    'sigma_clf_c': sigma_clf_c,
                    'sample': sample,
                    'type_am': type_am,
                    'perf_opt': perf_opt}
    ## Initializing object
    download_obj = DownloadManager(**input_dict)
    # Catalogue prefix
    download_prefix = download_obj._catl_prefix(catl_type=catl_type,
                                                catl_kind=catl_kind,
                                                perf_opt=perf_opt)
    # Checking that strings are equal
    assert(download_prefix == expected)


