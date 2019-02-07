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
__all__        = [  "url_checker",
                    "url_file_list",
                    "url_files_download"]

"""
Tools used to interact with web-related objects
"""

## Import modules
import os
import wget
from   bs4 import BeautifulSoup
import numpy as np
import requests
from   tqdm import tqdm
from   cosmo_utils.utils             import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error
from   cosmo_utils.utils             import file_utils as cfutils

## Functions

## Checking if URL is valid
def url_checker(url_str):
    """
    Checks if the URL is valid or not.

    Parameters
    -----------
    url_str : `str`
        URL of the website to evaluate.

    Raises
    ----------
    LSSUtils_Error : `Exception`
        Program exception if input parameters are accepted
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking input parameters
    if not (isinstance(url_str, str)):
        msg = '{0} `url_str` ({1}) is not a STRING!'.format(file_msg,
            type(url_str))
        raise LSSUtils_Error(msg)
    ##
    ## Checking Website
    request_url = requests.get(url_str)
    if (request_url.status_code != 200):
        msg = '{0} `url_str` ({1}) does not exist!'.format(file_msg, url_str)
        raise LSSUtils_Error(msg)

## Listing the files in a directory
def url_file_list(url, ext):
    """
    Lists the files from a URL taht have a specific file extension.

    Parameters
    -----------
    url : `str`
        String of the URL

    ext : `str`
        File extension of the files in the URL.

    Returns
    -----------
    files_arr : `numpy.ndarray`, shape (N,)
        Array of the file in `url` that match the file extension `ext`.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking for file type
    # 'URL'
    if not isinstance(url, str):
        msg = '{0} `url` ({1}) is not a valid type. It must be a STRING!'
        msg = msg.format(file_msg, type(url))
        raise TypeError(msg)
    # File extension
    if not isinstance(ext, str):
        msg = '{0} `ext` ({1}) is not a valid type. It must be a STRING!'
        msg = msg.format(file_msg, type(ext))
        raise TypeError(msg)
    ## Reformatting URL
    # Removing whitespaces
    url = url.strip()
    # Removing trailing slach
    if url.endswith('/'):
        url = url[:-1]
    # Checking if URL exists
    url_checker(url)
    # Reading in HTML from page
    page = requests.get(url).text
    # Converting to BeautifulSoup format
    soup = BeautifulSoup(page, 'html.parser')
    ## Obtaining list of files
    # Removing files that are NOT strings
    files_arr_pre = np.array([ xx.get('href') for xx in soup.find_all('a')
                                if isinstance(xx.get('href'), str)])
    # Only those finishing with certain extension
    files_pre_ext = np.array([xx for xx in files_arr_pre if xx.endswith(ext)])
    # Checking if file contains string 'http://'
    files_pre_web = np.array([(url + '/' + xx) if not ('//' in xx) else xx
                        for xx in files_pre_ext])
    # Sorting out file array
    files_arr = np.sort(files_pre_web)

    return files_arr

## Downloads the files from a URL to a local directory
def url_files_download(url, ext, outdir, check_exist=False, create_dir=False,
    remove_files=False, bar_opt='tqdm'):
    """
    Downloads the files from a URL to a local directory. The files that
    match a specific file extension, `ext`.

    Parameters
    -----------
    url : `str`
        String of the URL

    ext : `str`
        File extension of the files in the URL.

    outdir : `str`
        Path to the output directory. This is the directory, to which
        the files with extensions `ext` will be saved.

    check_exist : `bool`, optional
        If `True`, it checks for whether or not the file exists.
        This variable is set to `False` by default.

    create_dir : `bool`, optional
        If `True`, it creates the directory if it does not exist.
        This variable is set to `False` by default.

    remove_files : `bool`, optional
        If `True`, local files that are present that match the files at
        the URL will be replaced by the new versions. This variable is
        set to ``False`` by default.

    bar_opt : {'tqdm', 'native'}
        Option for which type of progress bar to use when downloading files.
        This variable is set to `tqdm` by default.
        Options:
            - 'tqdm' : Uses a tqdm-based progress bar
            - 'native': Used the wget-based native progress bar.
    """
    file_msg = fd.Program_Msg(__file__)
    ## Checking for file type
    # 'URL'
    if not isinstance(url, str):
        msg = '{0} `url` ({1}) is not a valid type. It must be a STRING!'
        msg = msg.format(file_msg, type(url))
        raise TypeError(msg)
    # File extension
    if not isinstance(ext, str):
        msg = '{0} `ext` ({1}) is not a valid type. It must be a STRING!'
        msg = msg.format(file_msg, type(ext))
        raise TypeError(msg)
    # Output directory
    if not isinstance(outdir, str):
        msg = '{0} `outdir` ({1}) is not a valid type. It must be a STRING!'
        msg = msg.format(file_msg, type(outdir))
        raise TypeError(msg)
    # `check_exist`
    if not (isinstance(check_exist, bool)):
        msg = '`check_exist` ({0}) must be of `boolean` type!'.format(
            type(check_exist))
        raise TypeError(msg)
    # `create_dir`
    if not (isinstance(create_dir, bool)):
        msg = '`create_dir` ({0}) must be of `boolean` type!'.format(
            type(create_dir))
        raise TypeError(msg)
    # `bar` - Type
    if not (isinstance(bar_opt, str)):
        msg = '`bar_opt` ({0}) must be of `boolean` type!'.format(
            type(bar_opt))
        raise TypeError(msg)
    # Progress bar - Value
    if not (bar_opt in ['tqdm', 'native']):
        msg = '{0} `bar_opt` ({1}) is not a valid option! Exiting'
        msg = msg.format(file_msg, bar_opt)
        raise LSSUtils_Error(msg)
    ##
    ## List of files in the URL
    files_arr = url_file_list(url, ext)
    # Creating directory
    if create_dir:
        cfutils.Path_Folder(outdir)
    # Check for its existence
    if check_exist:
        if not (os.path.exists(outdir)):
            msg = '`outdir` ({0}) was not found!'.format(
                outdir)
            raise FileNotFoundError(msg)
    ##
    ## Downloading files to output directory
    if len(files_arr) > 0:
        if (bar_opt == 'tqdm'):
            tqdm_desc = 'Downloading files: '
            for file_ii in tqdm(files_arr, desc=tqdm_desc):
                # Local file
                file_ii_local = os.path.join(   outdir,
                                                os.path.basename(file_ii))
                # Checking if local file exists
                if os.path.exists(file_ii_local):
                    if remove_files:
                        os.remove(file_ii_local)
                        wget_opt = True
                    else:
                        wget_opt = False
                else:
                    wget_opt = True
                ##
                ## Only downloading if necessary
                if wget_opt:
                    wget.download(file_ii, out=outdir, bar=None)
        elif (bar_opt == 'native'):
            for file_ii in files_arr:
                # Local file
                file_ii_local = os.path.join(   outdir,
                                                os.path.basename(file_ii))
                # Checking if local file exists
                if os.path.exists(file_ii_local):
                    if remove_files:
                        os.remove(file_ii_local)
                        wget_opt = True
                    else:
                        wget_opt = False
                else:
                    wget_opt = True
                ##
                ## Only downloading if necessary
                if wget_opt:
                    wget.download(file_ii, out=outdir)
    else:
        msg = '{0} Number of files is ZERO!'.format(file_msg)
        print(msg)
