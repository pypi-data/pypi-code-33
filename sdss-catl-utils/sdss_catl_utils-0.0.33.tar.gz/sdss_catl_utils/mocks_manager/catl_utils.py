#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018_12-18
# Last Modified: 2019-02-07
# Vanderbilt University
from __future__ import absolute_import, division, print_function 
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon, "]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  'catl_keys',
                    'catl_keys_prop',
                    'catl_clean',
                    'catl_clean_nmin',
                    'catl_prefix_str',
                    'catl_prefix_path',
                    'catl_prefix_main',
                    'check_input_params']

import os
import numpy as np
import pandas as pd
from collections import Counter

# Cosmo-Utils
from cosmo_utils.utils import file_utils   as cfutils

# Main Package
from sdss_catl_utils.mocks_manager import mocks_defaults as md
from sdss_catl_utils.custom_exceptions import SDSSCatlUtils_Error

## -- Functions and classes -- ##

# Catalogue keys - Main
def catl_keys(catl_kind='data', perf_opt=False, return_type='list'):
    """
    Provides a dictionary/list with the corresponding keys for 1) halo mass,
    2) Haloid/GroupID, 3) Group/Halo Galaxy-Type.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`, optional
        Type of the catalogue being analyzed. This variable corresponds
        to whether a ``real`` or ``synthetic/mock`` catalogue is being
        read/analyzed. This variable is set to ``data`` by default.

        Options:
            - ``data``: Catalogue(s) from the SDSS `real` catalogues
            - ``mocks``: Catalogue(s) from the `mock` catalogues.

    perf_opt : `bool`, optional
        If `True`, it returns the corresponding keys for a ``perfect``
        SDSS catalogue. This option only applies when ``catl_kind == 'mocks'``.

    return_type : {``list``, ``dict``} `str`, optional
        Type of output to be returned. This variable is set to `list` by
        default.

        Options:
            - ``list``: Returns the output as part of a list. The order of
                        the elements are: ``'group mass'``,
                        ``'groupid/haloid'``, and ``Group/Halo ID``.

    Returns
    ------------
    catl_objs : `dict` or `list`
        Dictionary or list of keys for ``group/halo mass``,
        ``group ID`` and ``galaxy type``
        columns in catalogues. This variable depends on the choice of
        `return_type`.

    Raises
    ------------
    SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
        Program exception if input parameters are `not` accepted.

    Examples
    ------------
    This function can be used for several different combinations of parameters.
    For example, if we wanted to analyze a ``data`` catalogue, and have this
    function return a ``list`` as the output, one could write::

        >>> catl_keys(catl_kind='data', return_type='list')
        ['M_h', 'groupid', 'galtype']

    This list corresponds to the 1) Group estimated mass, 2) Galaxy's group ID,
    and 3) Galaxy's group galaxy type.

    If instead, we wanted to analyze ``perfect mock catalogues``, we
    could write::

        >>> catl_keys(catl_kind='mocks', perf_opt=True, return_type='list')
        ['M_h', 'haloid', 'galtype']

    For more information and examples, please refer to
    :ref:`quickstart_getting_started`.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_kind` - Value
    catl_kind_arr = ['data', 'mocks']
    if not (catl_kind in catl_kind_arr):
        msg = '{0} `catl_kind` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_kind)
        raise SDSSCatlUtils_Error(msg)
    # `catl_kind` - Type
    if not (isinstance(catl_kind, str)):
        msg = '{0} `catl_kind` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_kind))
        raise TypeError(msg)
    # `perf_opt`  - Type
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(perf_opt))
        raise TypeError(msg)
    # `return_type` - Value
    return_type_arr = ['list', 'dict']
    if not (return_type in return_type_arr):
        msg = '{0} `return_type` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, return_type)
        raise SDSSCatlUtils_Error(msg)
    # `return_type` - Type
    if not (isinstance(return_type, str)):
        msg = '{0} `return_type` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(return_type))
        raise TypeError(msg)
    ##
    ## If analyzing real catalogues, setting ``perf_opt`` to False.
    if (catl_kind == 'data'):
        perf_opt = False
    ##
    ## Keys for the different sets of catalogues
    if (catl_kind == 'data'):
        (   gm_key,
            id_key,
            galtype) = ['M_h', 'groupid', 'galtype']
    elif (catl_kind == 'mocks'):
        if perf_opt:
            (   gm_key,
                id_key,
                galtype) = ['M_h', 'haloid', 'galtype']
        else:
            (   gm_key,
                id_key,
                galtype) = ['M_group', 'groupid', 'g_galtype']
    ##
    ## Determining which type of output to return
    if (return_type == 'list'):
        catl_objs = [gm_key, id_key, galtype]
    elif (return_type == 'dict'):
        catl_objs = {'gm_key': gm_key, 'id_key': id_key,
                        'galtype_key':galtype}

    return catl_objs

# Catalogue Keys - Galaxy properties
def catl_keys_prop(catl_kind='data', catl_info='memb', return_type='list'):
    """
    Provides a dictionary/list with the corresponding keys for 1) specific
    star formation rate (sSFR) and 2) stellar mass.

    Parameters
    ------------
    catl_kind : {``data``, ``mocks``} `str`, optional
        Type of the catalogue being analyzed. This variable corresponds
        to whether a ``real`` or ``synthetic/mock`` catalogue is being
        read/analyzed. This variable is set to ``data`` by default.

        Options:
            - ``data``: Catalogue(s) from the SDSS `real` catalogues
            - ``mocks``: Catalogue(s) from the `mock` catalogues.

    catl_info : {``memb``, ``groups``} `bool`, optional
        Option for which type of catalogue is being analyzed. This variable
        correspondos to whether a ``galaxy``-catalogue or a ``group``-catalogue
        is being analyzed. This variable is set to ``memb`` by default.

        Options:
            - ``memb``: Galaxy catalogue with the `member` galaxies of groups.
            - ``groups``: Catalogues with `group` information.

    return_type : {``list``, ``dict``} `str`, optional
        Type of output to be returned. This variable is set to `list` by
        default.

        Options:
            - ``list``: Returns the output as part of a list. The order of
                        the elements are: ``'group mass'``,
                        ``'groupid/haloid'``, and ``Group/Halo ID``.
    Returns
    ------------
    catl_objs : `dict` or `list`
        Dictionary or list of keys for ``logssfr`` and ``logmstar``
        columns in catalogues. This variable depends on the choice of
        `return_type`.

    Raises
    ------------
    SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
        Program exception if input parameters are `not` accepted.

    Examples
    ------------
    This function can be used for several different combinations of parameters.
    For example, if we wanted to analyze a ``data`` catalogue, and have this
    function return a ``list`` as the output, one could write::

        >>> catl_keys_prop(catl_kind='data', return_type='list')
        ['logssfr', 'logMstar_JHU']

    This list corresponds to the 1) `specific star formation rate` key and
    2) `stellar mass` key.

    If instead, we wanted to analyze a ``mock`` catalogue and return the
    appropriate keys for a ``group catalogue``, we could write::

        >>> catl_keys_prop(catl_kind='mocks', catl_info='groups')
        ['logssfr', 'logMstar']

    For more information and examples, please refer to
    :ref:`quickstart_getting_started`.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_kind` - Value
    catl_kind_arr = ['data', 'mocks']
    if not (catl_kind in catl_kind_arr):
        msg = '{0} `catl_kind` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_kind)
        raise SDSSCatlUtils_Error(msg)
    # `catl_kind` - Type
    if not (isinstance(catl_kind, str)):
        msg = '{0} `catl_kind` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_kind))
        raise TypeError(msg)
    # `catl_info` - Value
    catl_info_arr = ['memb', 'groups']
    if not (catl_info in catl_info_arr):
        msg = '{0} `catl_info` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_info)
        raise SDSSCatlUtils_Error(msg)
    # `catl_info` - Type
    if not (isinstance(catl_info, str)):
        msg = '{0} `catl_info` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_info))
        raise TypeError(msg)
    # `return_type` - Value
    return_type_arr = ['list', 'dict']
    if not (return_type in return_type_arr):
        msg = '{0} `return_type` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, return_type)
        raise SDSSCatlUtils_Error(msg)
    # `return_type` - Type
    if not (isinstance(return_type, str)):
        msg = '{0} `return_type` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(return_type))
        raise TypeError(msg)
    ##
    ## Dictionary with entries for ssfr and mstar for different combinations.
    keys_dict = {   'data_memb'   : ['logssfr', 'logMstar_JHU'],
                    'data_groups' : ['logssfr_tot', 'logMstar_tot'],
                    'mocks_memb'  : ['logssfr', 'logMstar'],
                    'mocks_groups': ['logssfr', 'logMstar']}
    # Deciding which key to use
    catl_key_str = '{0}_{1}'.format(catl_kind, catl_info)
    #
    # Determining which type of output to return
    if (return_type == 'list'):
        catl_objs = keys_dict[catl_key_str]
    elif (return_type == 'dict'):
        catl_objs = {   'logssfr_key' : keys_dict[catl_key_str][0],
                        'logmstar_key': keys_dict[catl_key_str][1]}

    return catl_objs

# Cleaning the catalogues from `bad` inputs
def catl_clean(catl_pd, catl_kind, catl_info='memb', reindex=True):
    """
    Cleans and removes the ``bad`` rows, i.e. those that contain `failed`
    entries for sSFR and Mstar.

    Parameters
    ------------
    catl_pd : `pandas.DataFrame`
        DataFrame containing the information about galaxies or galaxy groups.

    catl_kind : {``data``, ``mocks``} `str`, optional
        Type of the catalogue being analyzed. This variable corresponds
        to whether a ``real`` or ``synthetic/mock`` catalogue is being
        read/analyzed.

        Options:
            - ``data``: Catalogue(s) from the SDSS `real` catalogues
            - ``mocks``: Catalogue(s) from the `mock` catalogues.

    catl_info : {``memb``, ``groups``} `bool`, optional
        Option for which type of catalogue is being analyzed. This variable
        correspondos to whether a ``galaxy``-catalogue or a ``group``-catalogue
        is being analyzed. This variable is set to ``memb`` by default.

        Options:
            - ``memb``: Galaxy catalogue with the `member` galaxies of groups.
            - ``groups``: Catalogues with `group` information.
    
    reindex : `bool`, optional
        If `True`, the output catalogue is reindexed from the original dataframe
        `catl_pd`. This variable is set to `True` by default.

    Returns
    ----------
    catl_pd_mod : `pandas.DataFrame`
        Modified clean version of `catl_pd`. It removes the `failed`
        values.

    Raises
    ------------
    SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
        Program exception if input parameters are `not` accepted.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_pd` - Type
    if not (isinstance(catl_pd, pd.DataFrame)):
        msg = '{0} `catl_pd` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(catl_pd))
        raise TypeError(msg)
    # `catl_kind` - Value
    catl_kind_arr = ['data', 'mocks']
    if not (catl_kind in catl_kind_arr):
        msg = '{0} `catl_kind` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_kind)
        raise SDSSCatlUtils_Error(msg)
    # `catl_kind` - Type
    if not (isinstance(catl_kind, str)):
        msg = '{0} `catl_kind` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_kind))
        raise TypeError(msg)
    # `catl_info` - Value
    catl_info_arr = ['memb', 'groups']
    if not (catl_info in catl_info_arr):
        msg = '{0} `catl_info` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_info)
        raise SDSSCatlUtils_Error(msg)
    # `catl_info` - Type
    if not (isinstance(catl_info, str)):
        msg = '{0} `catl_info` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_info))
        raise TypeError(msg)
    # `reindex  ` - Type
    if not (isinstance(reindex, bool)):
        msg = '{0} `reindex` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(reindex))
        raise TypeError(msg)
    ##
    ## List of values that are considered `failed`. These values
    ## were assigned by the MPA-JHU group that developed the VAGC catalogue.
    ssfr_fail_arr = [0, -99, -999, np.nan]
    mstar_fail_arr= [-1, 0, np.nan]
    # Label for `ssfr` and `mstar`
    logssfr_key, logmstar_key = catl_keys_prop( catl_kind=catl_kind,
                                                catl_info=catl_info,
                                                return_type='list')
    ##
    ## Cleaning catalogue entries
    if (logmstar_key in catl_pd.columns.values):
        catl_pd_mod = catl_pd.loc[~catl_pd[logssfr_key].isin(ssfr_fail_arr) &
                                  ~catl_pd[logmstar_key].isin(mstar_fail_arr)]
    else:
        catl_pd_mod = catl_pd.loc[~catl_pd[logssfr_key].isin(ssfr_fail_arr)]
    #
    # Option if to reindex the new `clean` catalogue
    if reindex:
        catl_pd_mod.reset_index(drop=True, inplace=True)

    return catl_pd_mod

# Cleaning the catalogue from `fail` values and only include galaxies
# from groups larger than the number of galaxy threshold, i.e. ``nmin``.
def catl_clean_nmin(catl_pd, catl_kind, catl_info='memb', reindex=True,
    nmin=1, perf_opt=False):
    """
    Cleans and removed the ``bad`` rows with `failed` values, i.e.
    those that contain `failed` entries. This method also includes
    galaxies from groups above the ``nmin`` galaxy number threshold.

    Parameters
    --------------
    catl_pd : `pandas.DataFrame`
        DataFrame containing the information about galaxies or galaxy groups.

    catl_kind : {``data``, ``mocks``} `str`, optional
        Type of the catalogue being analyzed. This variable corresponds
        to whether a ``real`` or ``synthetic/mock`` catalogue is being
        read/analyzed.

        Options:
            - ``data``: Catalogue(s) from the SDSS `real` catalogues
            - ``mocks``: Catalogue(s) from the `mock` catalogues.

    catl_info : {``memb``, ``groups``} `bool`, optional
        Option for which type of catalogue is being analyzed. This variable
        correspondos to whether a ``galaxy``-catalogue or a ``group``-catalogue
        is being analyzed. This variable is set to ``memb`` by default.

        Options:
            - ``memb``: Galaxy catalogue with the `member` galaxies of groups.
            - ``groups``: Catalogues with `group` information.
    
    reindex : `bool`, optional
        If `True`, the output catalogue is reindexed from the original dataframe
        `catl_pd`. This variable is set to `True` by default.

    nmin : `int`, optional
        Minimum group richness to have in the (galaxy) group catalogue.
        This variable is set to ``1`` by default, and must be larger than
        `1`.

    perf_opt : `bool`, optional
        Option for using a `perfect` mock catalogue. This variable is set
        to `False` by default.

    Returns
    --------------
    catl_pd_mod : `pandas.DataFrame`
        Version of `catl_pd` after having removed the `failed` values
        of `sSFR` and `Mstar`, and also after having chosen only galaxies
        and groups with group richnesses larger than ``nmin``.

    Raises
    ------------
    SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
        Program exception if input parameters are `not` accepted.

    Examples
    ------------
    Before using this function, one needs to have read one of the
    (galaxy) group catalogues. If for example, one wants to create a
    new object from the ``data`` `real` SDSS catalogue with galaxies 
    from groups with ``n > 10``, one can do:

    >>> from cosmo_utils.utils import file_readers as cfr
    >>> from sdss_catl_utils.mocks_manager.catl_utils import catl_clean_nmin
    >>> nmin = 10 # Minimum number of galaxies in file
    >>> catl_pd = cfr.read_hdf5_file_to_pandas_DF('/path/to/file') # doctest: +SKIP
    >>> catl_mod = catl_clean_nmin(catl_pd, 'data', nmin=nmin) # doctest: +SKIP

    Now, the resulting catalogue will only include galaxies from groups
    with ``n > 10``.

    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_pd` - Type
    if not (isinstance(catl_pd, pd.DataFrame)):
        msg = '{0} `catl_pd` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(catl_pd))
        raise TypeError(msg)
    # `catl_kind` - Value
    catl_kind_arr = ['data', 'mocks']
    if not (catl_kind in catl_kind_arr):
        msg = '{0} `catl_kind` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_kind)
        raise SDSSCatlUtils_Error(msg)
    # `catl_kind` - Type
    if not (isinstance(catl_kind, str)):
        msg = '{0} `catl_kind` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_kind))
        raise TypeError(msg)
    # `catl_info` - Value
    catl_info_arr = ['memb', 'groups']
    if not (catl_info in catl_info_arr):
        msg = '{0} `catl_info` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, catl_info)
        raise SDSSCatlUtils_Error(msg)
    # `catl_info` - Type
    if not (isinstance(catl_info, str)):
        msg = '{0} `catl_info` ({1}) is not a valid input type!!'
        msg = msg.format(file_msg, type(catl_info))
        raise TypeError(msg)
    # `reindex  ` - Type
    if not (isinstance(reindex, bool)):
        msg = '{0} `reindex` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(reindex))
        raise TypeError(msg)
    # `nmin` - Type
    nmin_type_arr = (int, float)
    if (not isinstance(nmin, nmin_type_arr)):
        msg = '{0} `nmin` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(nmin))
        raise TypeError(msg)
    # `nmin` - Value
    if not (nmin >= 1):
        msg = '{0} `nmin` ({1}) must be larger than `1`!'
        msg = msg.format(file_m, nmin)
        raise SDSSCatlUtils_Error(msg)
    # `perf_opt` - Type
    if not (isinstance(perf_opt, bool)):
        msg = '{0} `perf_opt` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(perf_opt))
        raise TypeError(msg)
    ##
    ## Types of galaxies
    cens = int(1)
    nmin = int(nmin)
    # Keys for the catalogue
    gm_key, id_key, galtype_key = catl_keys(catl_kind, perf_opt=perf_opt)
    # Cleaning catalogue entries
    catl_pd_mod = catl_clean(   catl_pd,
                                catl_kind=catl_kind,
                                catl_info=catl_info,
                                reindex=reindex)
    # Choosing only galaxies in groups of richness >= `nmin`
    if (catl_info == 'groups'):
        if ('ngals' in catl_pd_mod.columns):
            catl_pd_mod_nmin = catl_pd_mod.loc[catl_pd_mod['ngals'] >= nmin]
        else:
            msg = '{0} Key `ngals` not found in DataFrame!'.format(file_msg)
            raise SDSSCatlUtils_Error(msg)
    elif (catl_info == 'memb'):
        # List of central galaxies
        cens_pd = catl_pd_mod.loc[(catl_pd_mod[galtype_key] == cens), id_key]
        catl_pd_cen = catl_pd_mod.loc[catl_pd_mod[id_key].isin(cens_pd)]
        # Counting the number of galaxies in each galaxy group and choosing
        # those above the `nmin` threshold.
        g_counts = Counter(catl_pd_cen[id_key].values)
        g_ngals  = [xx for xx in g_counts.keys() if g_counts[xx]>=nmin]
        # Selecting only galaxies with ``group_id`` in ``g_ngals``.
        catl_pd_mod_nmin = catl_pd_cen.loc[catl_pd_cen[id_key].isin(g_ngals)]
    #
    # Resetting index if necessary
    if reindex:
        catl_pd_mod_nmin.reset_index(drop=True, inplace=True)

    return catl_pd_mod_nmin

# Prefix string for the combination of input parameters for a catalog
def catl_prefix_str(catl_kind=md.catl_kind, hod_n=md.hod_n,
    halotype=md.halotype, clf_method=md.clf_method, clf_seed=md.clf_seed,
    dv=md.dv, sigma_clf_c=md.sigma_clf_c, sample=md.sample, type_am=md.type_am,
    perf_opt=md.perf_opt):
    """
    Prefix string for the combination of input parameters that describe
    a set of catalog(s).

    Parameters
    -----------
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

    Returns
    ---------
    catl_pre_str : `str`
        String of the prefix for each file based on `input` parameters.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_kind`
    check_input_params(catl_kind, 'catl_kind', check_type='type')
    check_input_params(catl_kind, 'catl_kind', check_type='vals')
    # `hod_n`
    check_input_params(hod_n, 'hod_n', check_type='type')
    check_input_params(hod_n, 'hod_n', check_type='vals')
    # `halotype`
    check_input_params(halotype, 'halotype', check_type='type')
    check_input_params(halotype, 'halotype', check_type='vals')
    # `clf_method`
    check_input_params(clf_method, 'clf_method', check_type='type')
    check_input_params(clf_method, 'clf_method', check_type='vals')
    # `clf_seed`
    check_input_params(clf_seed, 'clf_seed', check_type='type')
    # `dv`
    check_input_params(dv, 'dv', check_type='type')
    # `sigma_clf_c`
    check_input_params(sigma_clf_c, 'sigma_clf_c', check_type='type')
    # `sample`
    check_input_params(sample, 'sample', check_type='type')
    check_input_params(sample, 'sample', check_type='vals')
    # `type_am`
    check_input_params(type_am, 'type_am', check_type='type')
    check_input_params(type_am, 'type_am', check_type='vals')
    # `perf_opt`
    check_input_params(perf_opt, 'perf_opt', check_type='type')
    # Setting `perf_opt` to `False` if necessary
    if (catl_kind == 'data'):
        perf_opt = False
    # Extra parameters
    sample_Mr = 'Mr{0}'.format(sample)
    ##
    ## Parsing prefix path
    # `Data`
    if (catl_kind == 'data'):
        # List of variables to include in string
        catl_pre_arr = ['data', sample_Mr, type_am]
        # Prefix string
        catl_pre_str = '{0}_{1}_am_{2}'
        catl_pre_str = catl_pre_str.format(*catl_pre_arr)
    # `Mocks`
    if (catl_kind == 'mocks'):
        # List of variables to include in string
        catl_pre_arr = [sample_Mr,
                        halotype,
                        dv,
                        hod_n,
                        clf_seed,
                        clf_method,
                        sigma_clf_c,
                        type_am,
                        perf_opt]
        # Prefix string
        catl_pre_str  = '{0}_halo_{1}_dv_{2}_hn_{3}_clfs_{4}_clfm_{5}_'
        catl_pre_str += 'sigclf_{6}_am_{7}_pf_{8}'
        catl_pre_str  = catl_pre_str.format(*catl_pre_arr)

    return catl_pre_str

# Prefix path to catalogues
def catl_prefix_path(catl_kind=md.catl_kind, hod_n=md.hod_n,
    halotype=md.halotype, clf_method=md.clf_method, clf_seed=md.clf_seed,
    dv=md.dv, sigma_clf_c=md.sigma_clf_c, sample=md.sample, type_am=md.type_am,
    perf_opt=md.perf_opt):
    """
    Prefix of the paths based on the type of catalogues and input parameters
    chosen. It returns the typical path to the galaxy/group catalogues.

    Parameters
    -----------
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

    Returns
    ---------
    catl_prefix : `str`
        Prefix of the paths based on the type of catalogues and input
        parameters.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_kind`
    check_input_params(catl_kind, 'catl_kind', check_type='type')
    check_input_params(catl_kind, 'catl_kind', check_type='vals')
    # `hod_n`
    check_input_params(hod_n, 'hod_n', check_type='type')
    check_input_params(hod_n, 'hod_n', check_type='vals')
    # `halotype`
    check_input_params(halotype, 'halotype', check_type='type')
    check_input_params(halotype, 'halotype', check_type='vals')
    # `clf_method`
    check_input_params(clf_method, 'clf_method', check_type='type')
    check_input_params(clf_method, 'clf_method', check_type='vals')
    # `clf_seed`
    check_input_params(clf_seed, 'clf_seed', check_type='type')
    # `dv`
    check_input_params(dv, 'dv', check_type='type')
    # `sigma_clf_c`
    check_input_params(sigma_clf_c, 'sigma_clf_c', check_type='type')
    # `sample`
    check_input_params(sample, 'sample', check_type='type')
    check_input_params(sample, 'sample', check_type='vals')
    # `type_am`
    check_input_params(type_am, 'type_am', check_type='type')
    check_input_params(type_am, 'type_am', check_type='vals')
    # `perf_opt`
    check_input_params(perf_opt, 'perf_opt', check_type='type')
    # Setting `perf_opt` to `False` if necessary
    if (catl_kind == 'data'):
        perf_opt = False
    # Extra parameters
    sample_Mr = 'Mr{0}'.format(sample)
    ##
    ## Parsing prefix path
    # `Data`
    if (catl_kind == 'data'):
        catl_path_prefix = os.path.join('data',
                                        type_am,
                                        sample_Mr)
    # `Mocks`
    if (catl_kind == 'mocks'):
        catl_path_prefix = os.path.join(
                                'mocks',
                                'halos_{0}'.format(halotype),
                                'dv_{0}'.format(dv),
                                'hod_model_{0}'.format(hod_n),
                                'clf_seed_{0}'.format(clf_seed),
                                'clf_method_{0}'.format(clf_method),
                                'sigma_c_{0}'.format(sigma_clf_c),
                                type_am,
                                sample_Mr)

    return catl_path_prefix

# Catalogue prefix of the catalogues
def catl_prefix_main(catl_type='memb', catl_kind=md.catl_kind, hod_n=md.hod_n,
    halotype=md.halotype, clf_method=md.clf_method, clf_seed=md.clf_seed,
    dv=md.dv, sigma_clf_c=md.sigma_clf_c, sample=md.sample, type_am=md.type_am,
    perf_opt=md.perf_opt):
    """
    Prefix of the paths based on the type of catalogues and input parameters
    chosen.

    Parameters
    -----------
    catl_type : {``memb``, ``gal``, ``group``} `str`, optional
        Type of catalog to analyze. This option is set to ``memb`` by
        default.

        Options:
            - ``memb``: Analyzes the member galaxy catalogues of a group catalog
            - ``gal``: Analyzes a simple galaxy catalogue
            - ``group``: Analyzes a ``group`` galaxy catalogues with galaxy groups.

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

    Returns
    ---------
    catl_prefix : `str`
        Prefix of the paths based on the type of catalogues and input
        parameters.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ## Checking input parameters
    # `catl_type`
    check_input_params(catl_type, 'catl_type', check_type='type')
    check_input_params(catl_type, 'catl_type', check_type='vals')
    # `catl_kind`
    check_input_params(catl_kind, 'catl_kind', check_type='type')
    check_input_params(catl_kind, 'catl_kind', check_type='vals')
    # `hod_n`
    check_input_params(hod_n, 'hod_n', check_type='type')
    check_input_params(hod_n, 'hod_n', check_type='vals')
    # `halotype`
    check_input_params(halotype, 'halotype', check_type='type')
    check_input_params(halotype, 'halotype', check_type='vals')
    # `clf_method`
    check_input_params(clf_method, 'clf_method', check_type='type')
    check_input_params(clf_method, 'clf_method', check_type='vals')
    # `clf_seed`
    check_input_params(clf_seed, 'clf_seed', check_type='type')
    # `dv`
    check_input_params(dv, 'dv', check_type='type')
    # `sigma_clf_c`
    check_input_params(sigma_clf_c, 'sigma_clf_c', check_type='type')
    # `sample`
    check_input_params(sample, 'sample', check_type='type')
    check_input_params(sample, 'sample', check_type='vals')
    # `type_am`
    check_input_params(type_am, 'type_am', check_type='type')
    check_input_params(type_am, 'type_am', check_type='vals')
    # `perf_opt`
    check_input_params(perf_opt, 'perf_opt', check_type='type')
    ##
    ## Option for which type of catalogue to download
    catl_type_dict = {  'gal'  : 'galaxy_catalogues',
                        'memb' : 'member_galaxy_catalogues',
                        'group': 'group_galaxy_catalogues',
                        'perf_group': 'perfect_group_galaxy_catalogues',
                        'perf_memb' : 'perfect_member_galaxy_catalogues'}
    # Setting `perf_opt` to `False` if necessary
    if (catl_kind == 'data'):
        perf_opt = False
    # Deciding which folder to use
    if (catl_type == 'gal'):
        catl_type_str = 'gal'
    elif (catl_type in ['memb', 'group']):
        if perf_opt:
            # Member galaxies
            if (catl_type == 'memb'):
                catl_type_str = 'perf_memb'
            # Groups
            elif (catl_type == 'group'):
                catl_type_str = 'perf_group'
        else:
            # Member galaxies
            if (catl_type == 'memb'):
                catl_type_str = 'memb'
            # Groups
            elif (catl_type == 'group'):
                catl_type_str = 'group'
    #
    # Parsing prefix path
    catl_prefix_mod = catl_prefix_path(
                                    catl_kind=catl_kind,
                                    hod_n=hod_n,
                                    halotype=halotype,
                                    clf_method=clf_method,
                                    clf_seed=clf_seed,
                                    dv=dv,
                                    sigma_clf_c=sigma_clf_c,
                                    sample=sample,
                                    type_am=type_am,
                                    perf_opt=perf_opt)

    catl_prefix = os.path.join(catl_prefix_mod, catl_type_dict[catl_type_str])

    return catl_prefix

# Directory with accepted input parameters
def _get_input_params_dict():
    """
    Checks the input parameters to the class object.

    Returns
    ---------
    input_dict : `dict`
        Dictionary with the accepted ``type`` and ``value`` input
        parameters.
    """
    ## Dictionary with input variables
    # Variable types
    input_dict_type = { 'catl_kind'    : (str),
                        'hod_n'        : (int),
                        'halotype'     : (str),
                        'clf_method'   : (int),
                        'sigma_clf_c'  : (float),
                        'clf_seed'     : (int),
                        'dv'           : (int, float),
                        'sample'       : (str),
                        'type_am'      : (str),
                        'cosmo_choice' : (str),
                        'perf_opt'     : (bool),
                        'remove_files' : (bool),
                        'environ_name' : (str),
                        'catl_type'    : (str)}
    # Variable inputs
    input_dict_vals = { 'catl_kind'    : ['data', 'mocks'],
                        'hod_n'        : list(range(10)),
                        'halotype'     : ['fof', 'so'],
                        'clf_method'   : [1, 2, 3],
                        'sample'       : ['19', '20', '21'],
                        'type_am'      : ['mr', 'mstar'],
                        'cosmo_choice' : ['LasDamas', 'Planck'],
                        'catl_type'    : ['gal', 'memb', 'group']}
    # Merging dictionaries
    input_dict = {'type': input_dict_type, 'vals': input_dict_vals}

    return input_dict

# Checking input parameters to make sure they are `expected`
def check_input_params(input_var, var_name, check_type='type'):
    """
    Checks the type and/or values for different variables.

    Parameters
    ------------
    input_var : `int`, `float`, `bool`, `str`
        Input variable to be evaluated.

    var_name : `str`
        Name of the input parameter being evaluated. This variable name
        must correspond to one of the keys in the `type` or `vals`
        dictionaries.

    check_type : {``type``, ``vals``} `str`
        Type of check to perform. This variable is set to ``type`` by default.

        Options:
            - ``type``: It checks for the `type` of `input_var`.
            - ``vals``: It checks for the `value` of `input_var`.
    
    Raises
    ------------
    SDSSCatlUtils_Error : Exception from `~sdss_catl_utils.SDSSCatlUtils_Error`
        Program exception if input parameters are `not` accepted.
    """
    file_msg = cfutils.Program_Msg(__file__)
    ##
    ## Checking input parameters
    # `input_var` - Type
    input_var_arr = (int, float, bool, str)
    if not (isinstance(input_var, input_var_arr)):
        msg = '{0} `input_var` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(input_var))
        raise TypeError(msg)
    # `check_type` - Type
    if not (isinstance(check_type, str)):
        msg = '{0} `check_type` ({1}) is not a valid input type!'
        msg = msg.format(file_msg, type(check_type))
        raise TypeError(msg)
    # `check_type` - Value
    check_type_arr = ['type', 'vals']
    if not (check_type in check_type_arr):
        msg = '{0} `check_type` ({1}) is not a valid input value!'
        msg = msg.format(file_msg, check_type)
        raise ValueError(msg)
    ##
    ## Extracting input dictinaries
    input_dict = _get_input_params_dict()
    # Obtaining list of acceptable inputs
    if (check_type == 'type'):
        # Checking for input parameters - Type
        check_dict = input_dict[check_type]
        # Checking if key exists
        if (var_name in list(check_dict.keys())):
            if not (isinstance(input_var, check_dict[var_name])):
                msg = '{0} `{1}` ({2}) is not a valid input! Valid: `{3}` type'
                msg = msg.format(file_msg, var_name, type(input_var),
                        check_dict[var_name])
                raise TypeError(msg)
        else:
            # If `var_name` is not in dictionary
            msg = '{0} `{1}` is not in dictionary! Keys: `{2}`'
            msg = msg.format(file_msg, var_name, list(check_dict.keys()))
            raise KeyError(msg)
    elif (check_type == 'vals'):
        # Checking for input parameters - Values
        check_dict = input_dict[check_type]
        # Checking if key exists
        if (var_name in list(check_dict.keys())):
            if not (input_var in check_dict[var_name]):
                msg = '{0} `{1}` ({2}) is not a valid input! Valid: `{3}` type'
                msg = msg.format(file_msg, var_name, input_var,
                        check_dict[var_name])
                raise ValueError(msg)
        else:
            # If `var_name` is not in dictionary
            msg = '{0} `{1}` is not in dictionary! Keys: `{2}`'
            msg = msg.format(file_msg, var_name, list(check_dict.keys()))
            raise KeyError(msg)
