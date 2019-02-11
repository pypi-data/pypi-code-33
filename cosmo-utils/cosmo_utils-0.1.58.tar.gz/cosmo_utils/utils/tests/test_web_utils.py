#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-09
# Last Modified: 2018-05-09
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
"""
Set of test functions for the `web_utils` functions
"""

## Import modules
import pytest
from   cosmo_utils.utils import web_utils
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Testing URLS
urls_test_arr = [   'https://www.google.com/',
                    'http://www.pbworks.com/',
                    'https://vcalderon2009.github.io/',
                    'https://github.com/vcalderon2009/cosmo_utils/']
@pytest.mark.parametrize('url_str', urls_test_arr)
def test_url_checker(url_str):
    """
    Tests the function `cosmo_utils.utils.web_utils.url_checker` for input and
    output parameters

    Parameters
    -----------
    url_str : `str`
        URL of the website to evaluate.
    """
    ## Running function
    web_utils.url_checker(url_str)

## Testing URLS - Errors
urls_test_errors_arr = [    'https://www.google.com/1',
                            'http://www.pbworks.com/ber',
                            'https://vcalderon2009.github.io/testing',
                            'https://github.com/vcalderon2009/cosmo_utils/test']
@pytest.mark.parametrize('url_str', urls_test_errors_arr)
def test_url_checker(url_str):
    """
    Tests the function `cosmo_utils.utils.web_utils.url_checker` for input and
    output parameters

    Parameters
    -----------
    url_str : `str`
        URL of the website to evaluate.
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        web_utils.url_checker(url_str)

## Testing URLS - Errors - Input type
urls_test_types_err_arr = [1, 2, [1, 2, 3]]
@pytest.mark.parametrize('url_str', urls_test_types_err_arr)
def test_url_checker(url_str):
    """
    Tests the function `cosmo_utils.utils.web_utils.url_checker` for input and
    output parameters

    Parameters
    -----------
    url_str : `str`
        URL of the website to evaluate.
    """
    ## Running function
    with pytest.raises(LSSUtils_Error):
        web_utils.url_checker(url_str)
