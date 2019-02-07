#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-08
# Last Modified: 2018-05-08
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "catl_keys",
                    "catl_keys_prop",
                    "catl_sdss_dir",
                    "extract_catls",
                    "sdss_catl_clean",
                    "sdss_catl_clean_nmin",
                    "catl_sdss_merge"]

## Import modules
import os
from   collections       import Counter
import numpy as np
import pandas as pd
from   cosmo_utils.utils import file_utils   as fd
from   cosmo_utils.utils import work_paths   as wp
from   cosmo_utils.utils import file_readers as fr
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Catalogue Keys - Main
def catl_keys(catl_kind, perf_opt=False, return_type='list'):
    """
    Dictionary keys for the different types of catalogues

    Parameters
    ----------
    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    perf_opt : `bool`, optional
        Option for using a `perfect` mock catalogue.

    return_type : {'list', 'dict'} str, optional
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    Returns
    ----------
    catl_keys : python dictionary or array_like
        Dictionary/array with the proper keys for the catalogue(s).

        Order : 1) `gm_key`, 2) `id_key`, 3) `galtype_key`

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.

    Examples
    ----------
    >>> catl_keys('data', perf_opt=False, return_type='list')
    ['M_h', 'groupid', 'galtype']

    >>> catl_keys('mocks', perf_opt=True, return_type='list')
    ['M_h', 'haloid', 'galtype']
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_kind`
    if not (catl_kind in ['data', 'mocks']):
        msg = '{0} `catl_kind` ({1}) is not a valid input parameter!'.format(
            file_msg, catl_kind)
        raise LSSUtils_Error(msg)
    # `return_type`
    if not (return_type in ['list', 'dict']):
        msg = '{0} `return_type` ({1}) is not a valid input parameter'.format(
            file_msg, return_type)
        raise LSSUtils_Error(msg)
    # `perf_opt`
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) must be a boolean object!'.format(
            file_msg, type(perf_opt))
        raise LSSUtils_Error(msg)
    ##
    ## Perfect Catalogue
    if catl_kind == 'data':
        perf_opt = False
    ##
    ## Property keys
    if catl_kind == 'data':
        gm_key, id_key, galtype_key = ['M_h', 'groupid', 'galtype']
    elif catl_kind == 'mocks':
        if perf_opt:
            gm_key, id_key, galtype_key = ['M_h', 'haloid', 'galtype']
        else:
            gm_key, id_key, galtype_key = ['M_group', 'groupid', 'g_galtype']
    ##
    ## Saving values
    if return_type == 'dict':
        catl_objs = {   'gm_key'      : gm_key,
                        'id_key'      : id_key,
                        'galtype_key' : galtype_key}
    elif return_type == 'list':
        catl_objs = [   gm_key, id_key, galtype_key]

    return catl_objs

## Catalogue Keys - Properties
def catl_keys_prop(catl_kind, catl_info='members', return_type='list'):
    """
    Dictionary keys for the diffeent galaxy and group properties of
    catalogues.

    Parameters
    ------------
    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

        Options:
            - `members` : Member galaxies of group catalogues
            - `groups` : Catalogues with `group` information.

    return_type : {'list', 'dict'} str, optional
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    Return
    ------------
    catl_objs : python dictionary or array_like
        Dictionary/array with the proper keys for the catalogue(s).

        Order : 1) `ssfr_key`, 2) `mstar_key`

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.

    Examples
    ------------
    >>> catl_keys_prop('data')
    ['logssfr', 'logMstar_JHU']

    >>> catl_keys_prop('mocks', catl_info='groups', return_type='list')
    ['logssfr', 'logMstar']
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    catl_kind_valid   = ['data'   , 'mocks' ]
    catl_info_valid   = ['members', 'groups']
    return_type_valid = ['list'   , 'dict'  ]
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(
            file_msg, catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_info`
    if not (catl_info in catl_info_valid):
        msg = '{0} `catl_info` ({1}) is not a valid input!'.format(
            file_msg, catl_info)
        raise LSSUtils_Error(msg)
    # `return_type`
    if not (return_type in return_type_valid):
        msg = '{0} `return_type` ({1}) is not a valid input!'.format(
            file_msg, return_type)
        raise LSSUtils_Error(msg)
    #
    # Property keys
    #
    # Data
    if (catl_kind == 'data'):
        # Members
        if catl_info == 'members':
            # SSFR and Stellar mass
            logssfr_key, logmstar_key = ['logssfr', 'logMstar_JHU']
        # Groups
        if catl_info == 'groups':
            # SSFR and Stellar mass
            logssfr_key, logmstar_key = ['logssfr_tot', 'logMstar_tot']
    #
    # Mocks
    if (catl_kind == 'mocks'):
        # Members
        if catl_info == 'members':
            # SSFR and Stellar mass
            logssfr_key, logmstar_key = ['logssfr', 'logMstar']
        # Groups
        if catl_info == 'groups':
            # SSFR and Stellar mass
            logssfr_key, logmstar_key = ['logssfr', 'logMstar']
    #
    # Saving values
    if return_type == 'dict':
        catl_objs = {   'logssfr_key' : logssfr_key,
                        'logmstar_key': logmstar_key}
    elif return_type == 'list':
        catl_objs = [   logssfr_key, logmstar_key]

    return catl_objs

## Extracting path of synthetic catalogues
def catl_sdss_dir(catl_kind='data', catl_type='mr', sample_s='19',
    catl_info='members', halotype='fof', clf_method=3, hod_n=0, clf_seed=1235,
    dv=1.0, sigma_clf_c=0.1417, perf_opt=False, print_filedir=True):
    """
    Extracts the path to the synthetic catalogues.

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_type : {'mr', 'mstar'} str, optional
        Type of catalogue to use. It shows which abundance matching method
        was used for the CLF when assigning halo masses. This variable is
        set to 'mr' by default.

        Options:
            - `mr` : Uses r-band absolute magnitude
            - `mstar` : Uses stellar masses

    sample_s : {'19', '20', '21'} str, optional
        Volume-limited sample to use. This variable is set to '19' by default.

        Options:
            - '19' : Uses the Mr19 volume-limited sample, i.e. 'Consuelo'
            - '20' : Uses the Mr20 volume-limited sample, i.e. 'Esmeralda'
            - '21' : Uses the Mr21 volume-limited sample, i.e. 'Carmen'

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

        Options:
            - `members` : Member galaxies of group catalogues
            - `groups` : Catalogues with `group` information.

    halotype : {'fof', 'so'} str, optional
        Type of the dark matter halo of the simulation used to create the
        synthetic catalogues. This variable is set to `fof` by default.

        Options:
            - 'fof': Friends-of-Friends halos.
            - 'so' : Spherical overdensity halos.

    clf_method : {1, 2, 3} int, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable is set to `3` by default.

        Options:
            - `1` : Independent assigment of (g-r) color, sersic, and log(ssfr)
            - `2` : (g-r) decides active/passive designation and draw values
                    independently.
            - `3` : (g-r) decides active/passive designations, and
                    assigns other galaxy properties for that given galaxy.

    hod_n : {0, 1} int, optional
        HOD model to use. Only relevant when `catl_kind == mocks`.

    clf_seed : int, optional
        Seed used for the `CLF` random seed. This variable is set to `1235`
        by default.

    dv : float, optional
        Difference between galaxy and mass velocity profiles
        (v_g-v_c)/(v_m-v_c). This value is set to `1.0` by default.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies in the CLF.
        This variable is set to ``0.1417`` by default.

    perf_opt : `bool`, optional
        If True, it chooses to analyze the `perfect` set of synthetic
        catalogues. This variable is set to `False` by default.

    print_filedir : `bool`, optional
        If True, the output directory is printed onto the screen.

    Returns
    -----------
    catls_path : str
        Path to the desired set of synthetic catalogues.

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    catl_kind_valid  = ['data', 'mocks']
    catl_type_valid  = ['mr', 'mstar']
    sample_s_valid   = ['19', '20', '21']
    catl_info_valid  = ['members', 'groups']
    halotype_valid   = ['fof', 'so']
    clf_method_valid = [1, 2, 3]
    hod_n_valid      = np.arange(0, 20)
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(file_msg,
            catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_type`
    if not (catl_type in catl_type_valid):
        msg = '{0} `catl_type` ({1}) is not a valid input!'.format(file_msg,
            catl_type)
        raise LSSUtils_Error(msg)
    # `sample_s`
    if not (sample_s in sample_s_valid):
        msg = '{0} `sample_s` ({1}) is not a valid input!'.format(file_msg,
            sample_s)
        raise LSSUtils_Error(msg)
    # `catl_info`
    if not (catl_info in catl_info_valid):
        msg = '{0} `catl_info` ({1}) is not a valid input!'.format(file_msg,
            catl_info)
        raise LSSUtils_Error(msg)
    # `halotype`
    if not (halotype in halotype_valid):
        msg = '{0} `halotype` ({1}) is not a valid input!'.format(file_msg,
            halotype)
        raise LSSUtils_Error(msg)
    # `clf_method`
    if not (clf_method in clf_method_valid):
        msg = '{0} `clf_method` ({1}) is not a valid input!'.format(file_msg,
            clf_method)
        raise LSSUtils_Error(msg)
    # `hod_n`
    if not (hod_n in hod_n_valid):
        msg = '{0} `hod_n` ({1}) is not a valid input!'.format(file_msg,
            hod_n)
        raise LSSUtils_Error(msg)
    # `perf_opt`
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid type!'.format(file_msg,
            type(perf_opt))
        raise LSSUtils_Error(msg)
    # `print_filedir`
    if not (isinstance(print_filedir, bool)):
        msg = '{0} `print_filedir` ({1}) is not a valid type!'.format(file_msg,
            type(print_filedir))
        raise LSSUtils_Error(msg)
    # `dv`
    if not (dv > 0):
        msg = '{0} `dv` ({1}) must be larger than 0!'.format(file_msg, dv)
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Type
    if not (isinstance(sigma_clf_c, float)):
        msg = '{0} `sigma_clf_c` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(sigma_clf_c))
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Value
    if not (sigma_clf_c >= 0.):
        msg = '{0} `sigma_clf_c` ({1}) must be larger than 0!'
        msg = msg.format(file_msg, sigma_clf_c)
        raise LSSUtils_Error(msg)
    #
    # Type of catalogue
    if catl_info == 'members':
        catl_info_str = 'member_galaxy_catalogues'
    elif catl_info == 'groups':
        catl_info_str = 'group_galaxy_catalogues'
    #
    # Perfect catalogue
    if perf_opt:
        # Data
        if catl_kind == 'data':
            msg = '{0} Invalid `catl_kind` ({1}) for when `perf_opt == True'
            msg = msg.format(file_msg, catl_kind)
            raise LSSUtils_Error(msg)
        # Mocks
        catl_info_perf_str = 'perfect_{0}'.format(catl_info_str)
    else:
        # Mocks
        catl_info_perf_str = catl_info_str
    #
    # Extracting path of the files
    # Data
    if catl_kind == 'data':
        # Joining paths
        filedir = os.path.join( wp.get_output_path(),
                                'SDSS',
                                catl_kind,
                                catl_type,
                                'Mr' + sample_s,
                                catl_info_perf_str)
    # Mocks
    if catl_kind == 'mocks':
        # Joining paths
        filedir = os.path.join( wp.get_output_path(),
                                'SDSS',
                                catl_kind,
                                'halos_{0}'.format(halotype),
                                'dv_{0}'.format(dv),
                                'hod_model_{0}'.format(hod_n),
                                'clf_seed_{0}'.format(clf_seed),
                                'clf_method_{0}'.format(clf_method),
                                'sigma_c_{0}'.format(sigma_clf_c),
                                catl_type,
                                'Mr' + sample_s,
                                catl_info_perf_str)
    #
    # Making sure `filedir` exists
    if not (os.path.exists(filedir)):
        msg = '{0} `filedir` ({1}) does NOT exist! Check input variables'
        msg = msg.format(file_msg, filedir)
        raise LSSUtils_Error(msg)
    #
    # Printing out paths
    if print_filedir:
        print('{0} `filedir`: {1}'.format(file_msg, filedir))

    return filedir

# Extracting list of synthetic catalogues given input parameters
def extract_catls(catl_kind='data', catl_type='mr', sample_s='19',
    datatype='.hdf5', catl_info='members', halotype='fof', clf_method=3,
    hod_n=0, clf_seed=1235, dv=1.0, sigma_clf_c=0.1417, perf_opt=False,
    return_len=False, print_filedir=True):
    """
    Extracts a list of synthetic catalogues given input parameters

    Parameters
    ------------
    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_type : {'mr', 'mstar'} str, optional
        Type of catalogue to use. It shows which abundance matching method
        was used for the CLF when assigning halo masses. This variable is
        set to 'mr' by default.

        Options:
            - `mr` : Uses r-band absolute magnitude
            - `mstar` : Uses stellar masses

    sample_s : {'19', '20', '21'} str, optional
        Volume-limited sample to use. This variable is set to '19' by default.

        Options:
            - '19' : Uses the Mr19 volume-limited sample, i.e. 'Consuelo'
            - '20' : Uses the Mr20 volume-limited sample, i.e. 'Esmeralda'
            - '21' : Uses the Mr21 volume-limited sample, i.e. 'Carmen'

    datatype : {'.hdf5'} str, optional
        Data type of the files to be indexed in the folder. This variable
        is set to '.hdf5' by default.

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

        Options:
            - `members` : Member galaxies of group catalogues
            - `groups` : Catalogues with `group` information.

    halotype : {'fof', 'so'} str, optional
        Type of the dark matter halo of the simulation used to create the
        synthetic catalogues. This variable is set to `fof` by default.

        Options:
            - 'fof': Friends-of-Friends halos.
            - 'so' : Spherical overdensity halos.

    clf_method : {1, 2, 3} int, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable is set to `3` by default.

        Options:
            - `1` : Independent assigment of (g-r) color, sersic, and log(ssfr)
            - `2` : (g-r) decides active/passive designation and draw values
                    independently.
            - `3` : (g-r) decides active/passive designations, and
                    assigns other galaxy properties for that given galaxy.

    hod_n : {0, 1} int, optional
        HOD model to use. Only relevant when `catl_kind == mocks`.

    clf_seed : int, optional
        Seed used for the `CLF` random seed. This variable is set to `1235`
        by default.

    dv : float, optional
        Difference between galaxy and mass velocity profiles
        (v_g-v_c)/(v_m-v_c). This value is set to `1.0` by default.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies in the CLF.
        This variable is set to ``0.1417`` by default.

    perf_opt : `bool`, optional
        If True, it chooses to analyze the `perfect` set of synthetic
        catalogues. This variable is set to `False` by default.

    return_len : `bool`, optional
        If True, the function returns the total number of elements in
        the folder that match the criteria.

    print_filedir : `bool`, optional
        If True, the output directory is printed onto the screen.

    Returns
    ------------
    catl_arr : `numpy.ndarray`
        Array of elements/files matching the `datatype` type in the directory.

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking input parameters
    catl_kind_valid  = ['data', 'mocks']
    catl_type_valid  = ['mr', 'mstar']
    sample_s_valid   = ['19', '20', '21']
    catl_info_valid  = ['members', 'groups']
    halotype_valid   = ['fof', 'so']
    clf_method_valid = [1, 2, 3]
    hod_n_valid      = np.arange(0, 20)
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(file_msg,
            catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_type`
    if not (catl_type in catl_type_valid):
        msg = '{0} `catl_type` ({1}) is not a valid input!'.format(file_msg,
            catl_type)
        raise LSSUtils_Error(msg)
    # `sample_s`
    if not (sample_s in sample_s_valid):
        msg = '{0} `sample_s` ({1}) is not a valid input!'.format(file_msg,
            sample_s)
        raise LSSUtils_Error(msg)
    # `catl_info`
    if not (catl_info in catl_info_valid):
        msg = '{0} `catl_info` ({1}) is not a valid input!'.format(file_msg,
            catl_info)
        raise LSSUtils_Error(msg)
    # `halotype`
    if not (halotype in halotype_valid):
        msg = '{0} `halotype` ({1}) is not a valid input!'.format(file_msg,
            halotype)
        raise LSSUtils_Error(msg)
    # `clf_method`
    if not (clf_method in clf_method_valid):
        msg = '{0} `clf_method` ({1}) is not a valid input!'.format(file_msg,
            clf_method)
        raise LSSUtils_Error(msg)
    # `hod_n`
    if not (hod_n in hod_n_valid):
        msg = '{0} `hod_n` ({1}) is not a valid input!'.format(file_msg,
            hod_n)
        raise LSSUtils_Error(msg)
    # `perf_opt`
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid type!'.format(file_msg,
            type(perf_opt))
        raise LSSUtils_Error(msg)
    # `print_filedir`
    if not (isinstance(print_filedir, bool)):
        msg = '{0} `print_filedir` ({1}) is not a valid type!'.format(file_msg,
            type(print_filedir))
        raise LSSUtils_Error(msg)
    # `dv`
    if not (dv > 0):
        msg = '{0} `dv` ({1}) must be larger than 0!'.format(file_msg, dv)
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Type
    if not (isinstance(sigma_clf_c, float)):
        msg = '{0} `sigma_clf_c` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(sigma_clf_c))
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Value
    if not (sigma_clf_c >= 0.):
        msg = '{0} `sigma_clf_c` ({1}) must be larger than 0!'
        msg = msg.format(file_msg, sigma_clf_c)
        raise LSSUtils_Error(msg)
    # `return_len`
    if not (isinstance(return_len, bool)):
        msg = '{0} `return_len` ({1}) is not a valid type!'.format(file_msg,
            type(return_len))
        raise LSSUtils_Error(msg)
    # `datatype`
    if not (isinstance(datatype, str)):
        msg = '{0} `datatype` ({1}) is not a valid type!'.format(file_msg,
            type(datatype))
        raise LSSUtils_Error(msg)
    #
    # Extracting the path of the catalogues
    filedir = catl_sdss_dir(    catl_kind=catl_kind,
                                catl_type=catl_type,
                                sample_s=sample_s,
                                catl_info=catl_info,
                                halotype=halotype,
                                clf_method=clf_method,
                                hod_n=hod_n,
                                clf_seed=clf_seed,
                                dv=dv,
                                sigma_clf_c=sigma_clf_c,
                                perf_opt=perf_opt,
                                print_filedir=print_filedir)
    #
    # Converting to array
    catl_arr = np.sort(fd.Index(filedir, datatype))
    # Checking number of elements
    if len(catl_arr) == 0:
        msg = '{0} `catl_arr` contains 0 entries!'.format(file_msg)
        raise LSSUtils_Error(msg)
    #
    # Returning elements
    if return_len:
        return catl_arr, len(catl_arr)
    else:
        return catl_arr

# Cleaning the catalogue removing `failed` values
def sdss_catl_clean(catl_pd, catl_kind, catl_info='members', reindex=True):
    """
    Cleans the catalogue by removing `failed` values.

    Parameters
    -----------
    catl_pd : `pandas.DataFrame`
        Dataset with the catalogue information.

    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

        Options:
            - `members` : Member galaxies of group catalogues
            - `groups` : Catalogues with `group` information.

    reindex : `bool`, optional
        If True, the output catalogue is re-indexed.

    Return
    -----------
    catl_pd_clean : `pandas.DataFrame`
        Cleaned version of `catl_pd`, after having removed `failed` values.

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking input parameters
    catl_kind_valid  = ['data', 'mocks']
    catl_info_valid  = ['members', 'groups']
    # `catl_pd`
    if not (isinstance(catl_pd, pd.DataFrame)):
        msg = '{0} `catl_pd` ({1}) is not a valid type!'.format(file_msg,
            catl_pd)
        raise LSSUtils_Error(msg)
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(file_msg,
            catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_info`
    if not (catl_info in catl_info_valid):
        msg = '{0} `catl_info` ({1}) is not a valid input!'.format(file_msg,
            catl_info)
        raise LSSUtils_Error(msg)
    # `reindex
    if not (isinstance(reindex, bool)):
        msg = '{0} `reindex` ({1}) is not a valid type!'.format(file_msg,
            type(reindex))
        raise LSSUtils_Error(msg)
    #
    # Defining `failed` values
    ssfr_fail_arr  = [0, -99, -999, np.nan]
    mstar_fail_arr = [-1, 0, np.nan]
    #
    # Getting keys for catalogues
    (   logssfr_key   ,
        logmstar_key  ) = catl_keys_prop(   catl_kind=catl_kind,
                                            catl_info=catl_info,
                                            return_type='list')
    #
    # Cleaning catalogue entries
    #
    # Data
    if catl_kind == 'data':
        # Clean version
        catl_pd_clean = catl_pd[~catl_pd[logssfr_key].isin(ssfr_fail_arr) & \
                                ~catl_pd[logmstar_key].isin(mstar_fail_arr)]
    # Mocks
    if catl_kind == 'mocks':
        # Clean version
        catl_pd_clean = catl_pd[~catl_pd[logssfr_key].isin(ssfr_fail_arr)]
    #
    # Reindexing
    if reindex:
        catl_pd_clean.reset_index(inplace=True, drop=True)

    return catl_pd_clean

# Cleans dataset and includes only groups above a number of galaxy threshold
def sdss_catl_clean_nmin(catl_pd, catl_kind, catl_info='members', nmin=1,
    perf_opt=False):
    """
    Cleans the catalogue removing `failed` values, and only includes
    galaxies that are in groups/halos above a `nmin` threshold.

    Parameters
    -----------
    catl_pd : `pandas.DataFrame`
        Dataset with the catalogue information.

    catl_kind : {'data', 'mocks'} str, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

        Options:
            - `members` : Member galaxies of group catalogues
            - `groups` : Catalogues with `group` information.

    nmin : int, optional
        Minimum group richness to have in the (galaxy) group catalogue.
        This variable is set to `1` by default.

    perf_opt : `bool`, optional
        Option for using a `perfect` mock catalogue.

    Return
    -----------
    catl_pd_clean : `pandas.DataFrame`
        Cleaned version of `catl_pd` after having removed `failed` values,
        and having choosen only galaxies within groups above a group richness
        threshold of `nmin`.

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking input parameters
    catl_kind_valid  = ['data', 'mocks']
    catl_info_valid  = ['members', 'groups']
    # `catl_pd`
    if not (isinstance(catl_pd, pd.DataFrame)):
        msg = '{0} `catl_pd` ({1}) is not a valid type!'.format(file_msg,
            catl_pd)
        raise LSSUtils_Error(msg)
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(file_msg,
            catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_info`
    if not (catl_info in catl_info_valid):
        msg = '{0} `catl_info` ({1}) is not a valid input!'.format(file_msg,
            catl_info)
        raise LSSUtils_Error(msg)
    # `nmin`
    if not ((nmin > 0) and (isinstance(nmin, int))):
        msg = '{0} `nmin` must be an integer and have a value above `0`'
        msg = msg.format(file_msg)
        raise LSSUtils_Error(msg)
    # `perf_opt`
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid type!'.format(file_msg,
            type(perf_opt))
        raise LSSUtils_Error(msg)
    #
    # Types of galaxies
    cens = int(1)
    nmin = int(nmin)
    #
    # Getting keys for catalogue
    (   gm_key,
        id_key,
        galtype_key) = catl_keys(   catl_kind,
                                    return_type='list',
                                    perf_opt=perf_opt)
    
    # Cleaning catalogue entries
    catl_pd_clean_all = sdss_catl_clean(    catl_pd,
                                        catl_kind=catl_kind,
                                        catl_info=catl_info,
                                        reindex=True)
    # Choosing only galaxies in groups of richness >= `nmin`
    # Member galaxies
    if catl_info == 'members':
        # Centrals
        catl_pd_cens = catl_pd_clean_all.loc[(catl_pd_clean_all[galtype_key] == cens), id_key]
        catl_pd_cl   = catl_pd_clean_all[(catl_pd_clean_all[id_key].isin(catl_pd_cens))]
        # Group counts
        group_counts = Counter(catl_pd_cl[id_key])
        group_ngals  = np.array([xx for xx in group_counts.keys() if
                                group_counts[xx] >= nmin])
        # Cleaned version
        catl_pd_clean = catl_pd_cl[catl_pd_cl[id_key].isin(group_ngals)]
        catl_pd_clean.reset_index(inplace=True, drop=True)
    # Group catalogue
    if catl_info == 'groups':
        if ('ngals' in catl_pd_clean_all.columns.tolist()):
            catl_pd_clean = catl_pd_clean_all.loc[catl_pd_clean_all['ngals'] >= nmin]
            catl_pd_clean.reset_index(inplace=True, drop=True)
        else:
            msg = '{0} Key `ngals` not found in DataFrame ... Exiting!'
            msg = msg.format(file_msg)
            raise LSSUtils_Error(msg)

    return catl_pd_clean

# Merges the member and group catalogues for a given set of input parameters
def catl_sdss_merge(catl_pd_ii, catl_kind='data', catl_type='mr',
    sample_s='19', halotype='fof', clf_method=3, hod_n=0, clf_seed=1235,
    dv=1.0, sigma_clf_c=0.1417, perf_opt=False, return_memb_group=False, print_filedir=False):
    """
    Merges the member and group catalogues for a given set of input parameters,
    and returns a modified version of the galaxy group catalogues with added
    info about the galaxy groups.

    Parameters
    ------------
    catl_pd_ii : `int`
        Index of the catalogue to match,
        from :func:`~cosmo_utils.mock_catalogues.catls_utils.extract_catls`
        function.

    catl_kind : {'data', 'mocks'} `str`, optional
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_type : {'mr', 'mstar'} `str`, optional
        Type of catalogue to use. It shows which abundance matching method
        was used for the CLF when assigning halo masses. This variable is
        set to 'mr' by default.

        Options:
            - `mr` : Uses r-band absolute magnitude
            - `mstar` : Uses stellar masses

    sample_s : {'19', '20', '21'} str, optional
        Volume-limited sample to use. This variable is set to '19' by default.

        Options:
            - '19' : Uses the Mr19 volume-limited sample, i.e. 'Consuelo'
            - '20' : Uses the Mr20 volume-limited sample, i.e. 'Esmeralda'
            - '21' : Uses the Mr21 volume-limited sample, i.e. 'Carmen'

    halotype : {'fof', 'so'} str, optional
        Type of the dark matter halo of the simulation used to create the
        synthetic catalogues. This variable is set to `fof` by default.

        Options:
            - 'fof': Friends-of-Friends halos.
            - 'so' : Spherical overdensity halos.

    clf_method : {1, 2, 3} int, optional
        Method for assigning galaxy properties to mock galaxies.
        This variable is set to `3` by default.

        Options:
            - `1` : Independent assigment of (g-r) color, sersic, and log(ssfr)
            - `2` : (g-r) decides active/passive designation and draw values
                    independently.
            - `3` : (g-r) decides active/passive designations, and
                    assigns other galaxy properties for that given galaxy.

    hod_n : {0, 1} int, optional
        HOD model to use. Only relevant when `catl_kind == mocks`.

    clf_seed : int, optional
        Seed used for the `CLF` random seed. This variable is set to `1235`
        by default.

    dv : float, optional
        Difference between galaxy and mass velocity profiles
        (v_g-v_c)/(v_m-v_c). This value is set to `1.0` by default.

    sigma_clf_c : `float`, optional
        Value of the scatter in log(L) for central galaxies in the CLF.
        This variable is set to ``0.1417`` by default.

    perf_opt : `bool`, optional
        If True, it chooses to analyze the `perfect` set of synthetic
        catalogues. This variable is set to `False` by default.

    return_memb_group :  `bool`, optional
        If True, the function returns the member and group catalogues,
        along with the merged catalogue.
        It returns ``<memb_group_pd, memb_pd, group_pd>``

    print_filedir : `bool`, optional
        If True, the output directory is printed onto the screen.

    Return
    ------------
    memb_group_pd : `pandas.DataFrame`
        Combined version of the i-th member and group catalogues.
        It contains both galaxy and group information.

    memb_pd : `pandas.DataFrame`
        Catalogue of the member galaxies of the i-th catalogue.
        This catalogue contains information of the `member galaxies`.

    group_pd : `pandas.DataFrame`
        Catalogue of the groups of the i-th catalogue.
        This catalogue contains information of the `galaxy groups`.

    Raises
    ------------
    LSSUtils_Error : Exception from `LSSUtils_Error`
        Program exception if input parameters are accepted.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    catl_pd_ii_valid = (float, int, np.int64, np.int32, np.float32, np.float64)
    catl_kind_valid  = ['data', 'mocks']
    catl_type_valid  = ['mr', 'mstar']
    sample_s_valid   = ['19', '20', '21']
    halotype_valid   = ['fof', 'so']
    clf_method_valid = [1, 2, 3]
    hod_n_valid      = np.arange(0, 20)
    # `catl_pd_ii`
    if (isinstance(catl_pd_ii, catl_pd_ii_valid)):
        catl_pd_ii = int(catl_pd_ii)
    else:
        msg = '{0} `catl_pd_ii` ({1}) is not a valid input!'.format(file_msg,
            type(catl_pd_ii))
        raise LSSUtils_Error(msg)
    # `catl_kind`
    if not (catl_kind in catl_kind_valid):
        msg = '{0} `catl_kind` ({1}) is not a valid input!'.format(file_msg,
            catl_kind)
        raise LSSUtils_Error(msg)
    # `catl_type`
    if not (catl_type in catl_type_valid):
        msg = '{0} `catl_type` ({1}) is not a valid input!'.format(file_msg,
            catl_type)
        raise LSSUtils_Error(msg)
    # `sample_s`
    if not (sample_s in sample_s_valid):
        msg = '{0} `sample_s` ({1}) is not a valid input!'.format(file_msg,
            sample_s)
        raise LSSUtils_Error(msg)
    # `halotype`
    if not (halotype in halotype_valid):
        msg = '{0} `halotype` ({1}) is not a valid input!'.format(file_msg,
            halotype)
        raise LSSUtils_Error(msg)
    # `clf_method`
    if not (clf_method in clf_method_valid):
        msg = '{0} `clf_method` ({1}) is not a valid input!'.format(file_msg,
            clf_method)
        raise LSSUtils_Error(msg)
    # `dv`
    if not (dv > 0):
        msg = '{0} `dv` ({1}) must be larger than 0!'.format(file_msg, dv)
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Type
    if not (isinstance(sigma_clf_c, float)):
        msg = '{0} `sigma_clf_c` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(sigma_clf_c))
        raise LSSUtils_Error(msg)
    # `sigma_clf_c` - Value
    if not (sigma_clf_c >= 0.):
        msg = '{0} `sigma_clf_c` ({1}) must be larger than 0!'
        msg = msg.format(file_msg, sigma_clf_c)
        raise LSSUtils_Error(msg)
    # `hod_n`
    if not (hod_n in hod_n_valid):
        msg = '{0} `hod_n` ({1}) is not a valid input!'.format(file_msg,
            hod_n)
        raise LSSUtils_Error(msg)
    # `perf_opt`
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid type!'.format(file_msg,
            type(perf_opt))
        raise LSSUtils_Error(msg)
    # `return_memb_group`
    if not (isinstance(return_memb_group, bool)):
        msg = '{0} `return_memb_group` ({1}) is not a valid type!'.format(file_msg,
            type(return_memb_group))
        raise LSSUtils_Error(msg)
    # `print_filedir`
    if not (isinstance(print_filedir, bool)):
        msg = '{0} `print_filedir` ({1}) is not a valid type!'.format(file_msg,
            type(print_filedir))
        raise LSSUtils_Error(msg)
    #
    # Extracting catalogues given input parameters
    (   memb_arr,
        memb_len) = extract_catls(  catl_kind=catl_kind,
                                    catl_type=catl_type,
                                    sample_s=sample_s,
                                    halotype=halotype,
                                    clf_method=clf_method,
                                    hod_n=hod_n,
                                    clf_seed=clf_seed,
                                    dv=dv,
                                    sigma_clf_c=sigma_clf_c,
                                    perf_opt=perf_opt,
                                    catl_info='members',
                                    return_len=True,
                                    print_filedir=print_filedir)
    # Checking number of catalogues
    if catl_pd_ii > (memb_len - 1):
        msg = '{0} `catl_pd_ii` ({1}) is OUT of range ({2})!'.format(
            file_msg, catl_pd_ii, memb_len)
        raise LSSUtils_Error(msg)
    #
    # Extracting group catalogue
    # i-th Galaxy catalogue
    memb_path = memb_arr[catl_pd_ii]
    # i-th Galaxy Group catalogue
    group_path = catl_sdss_dir( catl_kind=catl_kind,
                                catl_type=catl_type,
                                sample_s=sample_s,
                                halotype=halotype,
                                clf_method=clf_method,
                                dv=dv,
                                sigma_clf_c=sigma_clf_c,
                                hod_n=hod_n,
                                clf_seed=clf_seed,
                                perf_opt=perf_opt,
                                catl_info='groups',
                                print_filedir=print_filedir)
    #
    # Paths to catalogue
    # Mocks
    if catl_kind == 'mocks':
        group_path  = os.path.join(group_path, 
                        os.path.basename(memb_path).replace('memb', 'group'))
    # Data
    if catl_kind == 'data':
        group_path = os.path.join(group_path,
                        os.path.basename(memb_path).replace('Gals', 'Group'))
    # Checking that file exists
    fd.File_Exists(group_path)
    ##
    ## Reading in Catalogues
    memb_pd  = fr.read_hdf5_file_to_pandas_DF(memb_path )
    group_pd = fr.read_hdf5_file_to_pandas_DF(group_path)
    ## Keys for the catalogues
    (   gm_key,
        id_key,
        galtype_key) = catl_keys(   catl_kind,
                                    perf_opt=perf_opt,
                                    return_type='list')
    ## Matching keys from Group catalogue
    if len(np.unique(memb_pd[id_key])) == len(np.unique(group_pd[id_key])):
        # Group column names
        group_colnames = np.sort(group_pd.columns.values)
        ## Sorting `memb_pd` by `id_key`
        # Member catalogue
        memb_pd.sort_values(by=id_key, inplace=True)
        memb_pd.reset_index(inplace=True, drop=True)
        # Group catalogue
        group_pd.sort_values(by=id_key, inplace=True)
        group_pd.reset_index(inplace=True, drop=True)
        ## Renaming columns
        g_colnames_dict = {ii: 'GG_' + ii for ii in group_colnames}
        group_pd.rename(columns=g_colnames_dict, inplace=True)
        group_pd.rename(columns={'GG_' + id_key: id_key}, inplace=True)
        ##
        ## Merging the 2 DataFrames
        memb_group_pd = pd.merge(   left=memb_pd   ,
                                    right=group_pd ,
                                    how='left'     ,
                                    left_on=id_key ,
                                    right_on=id_key)
    else:
        msg  = '{0} Lengths of the 2 DataFrames (`memb_pd`, `group_pd`) '
        msg += 'do not match!'
        msg  = msg.format(file_msg)
        raise LSSUtils_Error(msg)
    ##
    ## Returning DataFrames
    if return_memb_group:
        return_obj = (memb_group_pd, memb_pd, group_pd)
    else:
        return_obj = memb_group_pd

    return return_obj
