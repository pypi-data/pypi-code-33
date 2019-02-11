#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-08
# Last Modified: 2018-05-08
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
"""
Set of test functions for the `catls_utils` functions
"""

## Import modules
import numpy as np
import pytest
from   cosmo_utils.mock_catalogues import catls_utils
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Test `catl_keys` function - Types
catl_keys_types_arr = [     ('data' , 'list', 3, list),
                            ('data' , 'dict', 3, dict),
                            ('mocks', 'list', 3, list),
                            ('mocks', 'dict', 3, dict) ]
@pytest.mark.parametrize('catl_kind, return_type, nelem, expected',
    catl_keys_types_arr)
def test_catl_keys_types_nelem(catl_kind, return_type, nelem, expected):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys` for input and 
    output variables.

    It verifies the `type` of the output returned by the function.

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    return_type : {'list', 'dict'} str
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    nelem : int
        Expected number of elements inside the object returned by the function.

    expected : str
        Expected type of element from the `catl_keys` function
    """
    ## Constants
    perf_opt = False
    ## Running element
    output = catls_utils.catl_keys(catl_kind, return_type=return_type,
        perf_opt=perf_opt)
    ## Comparing against `expected` value - Type
    assert(isinstance(output, expected))
    ## Checking number of elements returned
    if isinstance(output, list):
        assert(len(output) == nelem)
    elif isinstance(output, dict):
        assert(len(output.keys()) == nelem)

## Test `catl_keys` function - Outputs
catl_keys_return_arr = [ 'list' , 'dict']
catl_keys_output_arr = [('data' , False, ['M_h', 'groupid', 'galtype']),
                        ('data' , False, ['M_h', 'groupid', 'galtype']),
                        ('mocks', False, ['M_group', 'groupid', 'g_galtype']),
                        ('mocks', True, ['M_h', 'haloid', 'galtype'])]
@pytest.mark.parametrize('return_type', catl_keys_return_arr)
@pytest.mark.parametrize('catl_kind, perf_opt, expected', catl_keys_output_arr)
def test_catl_keys_outputs(catl_kind, perf_opt, return_type, expected):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys` for input and 
    output variables.

    It verifies the output returned by the function.

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    perf_opt : `bool`, optional
        Option for using a `perfect` mock catalogue.

    return_type : {'list', 'dict'} str
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    expected : str
        Expected type of element from the `catl_keys` function
    """
    ## Running element
    output = catls_utils.catl_keys(catl_kind, perf_opt=perf_opt, 
        return_type=return_type)
    ## Comparing against `expected` value - Output
    if isinstance(output, list):
        np.testing.assert_equal(output, expected)
    elif isinstance(output, dict):
        out_keys = ['gm_key', 'id_key', 'galtype_key']
        out_vals = [output[xx] for xx in out_keys]
        np.testing.assert_equal(out_vals, expected)

## Test `catl_keys` function - Errors - `catl_kind`
catl_keys_catl_kind_arr = [ 'data1', 'mocks1', 'NoMethod']
catl_keys_catl_perf_arr = [ True, False]
catl_keys_return_arr    = [ 'list' , 'dict']
@pytest.mark.parametrize('catl_kind', catl_keys_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_return_arr)
@pytest.mark.parametrize('perf_opt', catl_keys_catl_perf_arr)
def test_catl_keys_catl_kind_errors(catl_kind, perf_opt, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys` for input and 
    output variables.

    It verifies if errors are raised when `catl_kind` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys(catl_kind, perf_opt=perf_opt,
            return_type=return_type)

## Test `catl_keys` function - Errors - `return_type`
catl_keys_catl_kind_arr = ['data', 'mocks']
catl_keys_catl_perf_arr = [True, False]
catl_keys_return_arr    = [ 'list_no' , 'dict1', 'NoMethod']
@pytest.mark.parametrize('catl_kind', catl_keys_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_return_arr)
@pytest.mark.parametrize('perf_opt', catl_keys_catl_perf_arr)
def test_catl_keys_catl_kind_errors(catl_kind, perf_opt, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys` for input and 
    output variables.

    It verifies if errors are raised when `catl_kind` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys(catl_kind, perf_opt=perf_opt,
            return_type=return_type)

## Test `catl_keys` function - Errors - `return_type`
catl_keys_catl_kind_arr = ['data', 'mocks']
catl_keys_catl_perf_arr = [ 'NotBoolean', 1, 'mark', 1.2]
catl_keys_return_arr    = [ 'list' , 'dict']
@pytest.mark.parametrize('catl_kind', catl_keys_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_return_arr)
@pytest.mark.parametrize('perf_opt', catl_keys_catl_perf_arr)
def test_catl_keys_catl_kind_errors(catl_kind, perf_opt, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys` for input and 
    output variables.

    It verifies if errors are raised when `catl_kind` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys(catl_kind, perf_opt=perf_opt,
            return_type=return_type)

#########-------------------------------------------------------------#########

## Test `catl_keys_prop` function - Types
catl_keys_prop_info_arr  = ['members', 'groups']
catl_keys_prop_types_arr = [('data' , 'list', 2, list),
                            ('data' , 'dict', 2, dict),
                            ('mocks', 'list', 2, list),
                            ('mocks', 'dict', 2, dict) ]
@pytest.mark.parametrize('catl_info', catl_keys_prop_info_arr)
@pytest.mark.parametrize('catl_kind, return_type, nelem, expected',
    catl_keys_prop_types_arr)
def test_catl_keys_prop_types_nelem(catl_kind, catl_info, return_type, nelem,
    expected):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys_prop` for input and 
    output variables.

    It verifies the `type` of the output returned by the function.

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

    return_type : {'list', 'dict'} str
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    nelem : int
        Expected number of elements inside the object returned by the function.

    expected : str
        Expected type of element from the `catl_keys_prop` function
    """
    ## Running element
    output = catls_utils.catl_keys_prop(catl_kind, catl_info=catl_info,
        return_type=return_type)
    ## Comparing against `expected` value - Type
    assert(isinstance(output, expected))
    ## Checking number of elements returned
    if isinstance(output, list):
        assert(len(output) == nelem)
    elif isinstance(output, dict):
        assert(len(output.keys()) == nelem)

## Test `catl_keys_prop` function - Outputs
catl_keys_prop_return_arr = [ 'list' , 'dict']
catl_keys_prop_output_arr = [('data' , 'members', ['logssfr'    , 'logMstar_JHU']),
                        ('data' , 'groups' , ['logssfr_tot', 'logMstar_tot']),
                        ('mocks', 'members', ['logssfr'    , 'logMstar']),
                        ('mocks', 'groups' , ['logssfr'    , 'logMstar'])]
@pytest.mark.parametrize('return_type', catl_keys_prop_return_arr)
@pytest.mark.parametrize('catl_kind, catl_info, expected', catl_keys_prop_output_arr)
def test_catl_keys_prop_outputs(catl_kind, catl_info, return_type, expected):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys_prop` for input and 
    output variables.

    It verifies the output returned by the function.

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues

    catl_info : {'members', 'groups'} str, optional
        Option for which kind of catalogues to use.

    return_type : {'list', 'dict'} str
        Type of output to the be returned. This variable is set to `list`
        by default.

        Options:
            - 'list' : Returns the values as part of a list
            - 'dict' : Returns the values as part of a python dictionary

    expected : str
        Expected type of element from the `catl_keys_prop` function
    """
    ## Running element
    output = catls_utils.catl_keys_prop(catl_kind, catl_info=catl_info, 
        return_type=return_type)
    ## Comparing against `expected` value - Output
    if isinstance(output, list):
        np.testing.assert_equal(output, expected)
    elif isinstance(output, dict):
        out_keys = ['logssfr_key', 'logmstar_key']
        out_vals = [output[xx] for xx in out_keys]
        np.testing.assert_equal(out_vals, expected)

## Test `catl_keys_prop` function - Errors - `catl_kind`
catl_keys_prop_catl_kind_arr = [ 'data1', 'mocks1', 'NoMethod']
catl_keys_prop_return_arr    = [ 'list' , 'dict']
catl_keys_prop_catl_info_arr = [ 'members', 'groups']
@pytest.mark.parametrize('catl_kind', catl_keys_prop_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_prop_return_arr)
@pytest.mark.parametrize('catl_info', catl_keys_prop_catl_info_arr)
def test_catl_keys_prop_catl_kind_errors(catl_kind, catl_info, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys_prop` for input and 
    output variables.

    It verifies if errors are raised when `catl_kind` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys_prop(catl_kind, catl_info=catl_info,
            return_type=return_type)

## Test `catl_keys_prop` function - Errors - `catl_info`
catl_keys_prop_catl_kind_arr = [ 'data', 'mocks']
catl_keys_prop_return_arr    = [ 'list' , 'dict']
catl_keys_prop_catl_info_arr = [ 'members_no', 'groups_Invalid', 1, 1.2]
@pytest.mark.parametrize('catl_kind', catl_keys_prop_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_prop_return_arr)
@pytest.mark.parametrize('catl_info', catl_keys_prop_catl_info_arr)
def test_catl_keys_prop_catl_info_errors(catl_kind, catl_info, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys_prop` for input and 
    output variables.

    It verifies if errors are raised when `catl_info` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys_prop(catl_kind, catl_info=catl_info,
            return_type=return_type)

## Test `catl_keys_prop` function - Errors - `return_type`
catl_keys_prop_catl_kind_arr = [ 'data', 'mocks']
catl_keys_prop_return_arr    = [ 'list_no' , 'dict1', 'NoMethod']
catl_keys_prop_catl_info_arr = [ 'members', 'groups']
@pytest.mark.parametrize('catl_kind', catl_keys_prop_catl_kind_arr)
@pytest.mark.parametrize('return_type', catl_keys_prop_return_arr)
@pytest.mark.parametrize('catl_info', catl_keys_prop_catl_info_arr)
def test_catl_keys_prop_return_type_errors(catl_kind, catl_info, return_type):
    """
    Tests the function:
        cosmo_utils.mock_catalogues.catls_utils.catl_keys_prop` for input and 
    output variables.

    It verifies if errors are raised when `return_type` is incorrect

    Parameters
    -----------
    catl_kind : {'data', 'mocks'} str
        Type of catalogue to use. This variable is set to `data` by default.

        Options:
            - `data` : catalogues come from SDSS `real` catalogue
            - `mocks` : catalogue come from SDSS `mock` catalogues
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        output = catls_utils.catl_keys_prop(catl_kind, catl_info=catl_info,
            return_type=return_type)


#########-------------------------------------------------------------#########
















