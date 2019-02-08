#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-12-28
# Last Modified: 2018-12-28
# Vanderbilt University
from __future__ import absolute_import, division, print_function 
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon, 2018"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
"""
Set of test functions for the `catl_models` functions
"""

import numpy as np
import pytest
from sdss_catl_utils.models import catl_models
from sdss_catl_utils.custom_exceptions import SDSSCatlUtils_Error

## Functions

#########-------------------------------------------------------------#########
#########-------------------------------------------------------------#########

#### ------------------- Test `CatlUtils` function - Types ----------------- ##

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

@pytest.mark.parametrize('catl_kind', catl_kind_arr)
@pytest.mark.parametrize('hod_n', hod_n_arr)
@pytest.mark.parametrize('halotype', halotype_arr)
@pytest.mark.parametrize('clf_method', clf_method_arr)
@pytest.mark.parametrize('clf_seed', clf_seed_arr)
@pytest.mark.parametrize('dv', dv_arr)
@pytest.mark.parametrize('sample', sample_arr)
@pytest.mark.parametrize('type_am', type_am_arr)
@pytest.mark.parametrize('cosmo_choice', cosmo_choice_arr)
@pytest.mark.parametrize('perf_opt', perf_opt_arr)
@pytest.mark.parametrize('remove_files', remove_files_arr)
@pytest.mark.parametrize('environ_name', environ_name_arr)
def test_CatlUtils_inputs_types(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name):
    """
    Checks the function `~sdss_catl_utils.models.catl_models.CatlUtils`
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
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    obj_ii = catl_models.CatlUtils(**input_dict)

#### ------------- Test `CatlUtils` function - Error - Types --------------- ##

input_arr_type = [\
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 1),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, 'str', 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', 'str', True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 123, True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 1000, 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, 1, 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 'test', '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, '1', 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', '1', 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 10, 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', '2', 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        (32, 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a')]
input_str_type  = 'catl_kind, hod_n, halotype, clf_method, clf_seed, dv, sample, '
input_str_type += 'type_am, cosmo_choice, perf_opt, remove_files, environ_name'
@pytest.mark.parametrize(input_str_type, input_arr_type)
def test_CatlUtils_inputs_err_type(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name):
    """
    Checks the function `~sdss_catl_utils.models.catl_models.CatlUtils`
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
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    with pytest.raises(TypeError):
        obj_ii = catl_models.CatlUtils(**input_dict)

#### ------------- Test `CatlUtils` function - Error - Values --------------- ##

input_arr_vals = [\
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'LasDamas1', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck1', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mr2', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '19', 'mstar2', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, '191', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 1, 1, 0.6, 'a', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 0, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 5, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so', 4, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'so1', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 1, 'fof2', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 12, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data', 98, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('data_1', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a'),
        ('mocks2', 1, 'so', 1, 1, 0.6, '19', 'mr', 'Planck', True, True, 'a')]
input_str_vals  = 'catl_kind, hod_n, halotype, clf_method, clf_seed, dv, sample, '
input_str_vals += 'type_am, cosmo_choice, perf_opt, remove_files, environ_name'
@pytest.mark.parametrize(input_str_vals, input_arr_vals)
def test_CatlUtils_inputs_err_vals(catl_kind, hod_n, halotype, clf_method,
    clf_seed, dv, sample, type_am, cosmo_choice, perf_opt, remove_files,
    environ_name):
    """
    Checks the function `~sdss_catl_utils.models.catl_models.CatlUtils`
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
                    'sample': sample,
                    'type_am': type_am,
                    'cosmo_choice': cosmo_choice,
                    'perf_opt': perf_opt,
                    'remove_files': remove_files,
                    'environ_name': environ_name}
    ## Running function
    with pytest.raises(ValueError):
        obj_ii = catl_models.CatlUtils(**input_dict)

#### ------------- Test `SDSSConformity` function - Error - Type --------- ##
def test_SDSSConformity_paramdict():
    """
    Checks the function `~sdss_catl_utils.models.catl_models.SDSSConformity`
    for initialization, and that it returns a `dict` when retrieving the
    set of input parameters
    """
    catl_obj = catl_models.SDSSConformity()
    assert(isinstance(catl_obj.param_dict, dict))
    assert(isinstance(catl_obj.publications, list))
    assert(isinstance(catl_obj.github_url, list))
    assert(isinstance(catl_obj.analysis_docs, list))


#### ------------- Test `SDSSCatlAnalysis` function - Error - Values --------- ##
def test_SDSSCatlAnalysis_paramdict():
    """
    Checks the function `~sdss_catl_utils.models.catl_models.SDSSCatlAnalysis`
    for initialization, and that it returns a `dict` when retrieving the
    set of input parameters
    """
    catl_obj = catl_models.SDSSCatlAnalysis()
    assert(isinstance(catl_obj.param_dict, dict))
    # assert(isinstance(catl_obj.publications, list))
    assert(isinstance(catl_obj.github_url, list))
    # assert(isinstance(catl_obj.analysis_docs, list))

#### ------------- Test `SDSSMLAnalysis` function - Error - Values --------- ##
def test_SDSSMLAnalysis_paramdict():
    """
    Checks the function `~sdss_catl_utils.models.catl_models.SDSSMLAnalysis`
    for initialization, and that it returns a `dict` when retrieving the
    set of input parameters
    """
    catl_obj = catl_models.SDSSMLAnalysis()
    assert(isinstance(catl_obj.param_dict, dict))
    # assert(isinstance(catl_obj.publications, list))
    assert(isinstance(catl_obj.github_url, list))
    # assert(isinstance(catl_obj.analysis_docs, list))