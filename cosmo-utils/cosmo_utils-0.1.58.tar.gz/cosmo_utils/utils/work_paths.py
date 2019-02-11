#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-04-28
# Last Modified: 2018-04-28
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "git_root_dir",
                    "cookiecutter_paths",
                    "get_code_c",
                    "get_sdss_catl_dir",
                    "get_output_path"]
"""
Set of files to facilitate paths
"""

## Import modules
import os
import git
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

## Getting the Git path of the repository
def git_root_dir(path='./'):
    """
    Determines the path to the main .git folder of the project.

    Taken from:
        - https://goo.gl/46y9v1

    Parameters
    ----------
    path : str, optional
        Path to the file within the `.git` repository

    Return
    ----------
    gitroot : `git.repo.base.Repo`
        Git object that contains the parent git directory
    """
    # Creating instance of Git Repo
    gitrepo = git.Repo(os.path.abspath(path), search_parent_directories=True)
    # Git Root parent directory
    gitroot = gitrepo.git.rev_parse("--show-toplevel")

    return gitroot

## Main Cookiecutter Path directories
def cookiecutter_paths(path='./'):
    """
    Paths to main folders in the `Data Science` cookiecutter template.
    This structure was taken from :
    - https://drivendata.github.io/cookiecutter-data-science/

    Parameters
    ----------
    path : str, optional
        Path to the file within the `.git` repository

    Return
    ----------
    param_dict : python dictionary
        Dictionary with info of the project that uses the Data Science
        cookiecutter template.

    Raises
    ----------
    LSSUtils_Error : exception
        If `path` is not within a .git directory, it raises an error.
    """
    # Base Path
    base_dir = git_root_dir(path) + '/'
    # Checking that directory exists
    if os.path.exists(base_dir):
        # Plot Directory
        plot_dir = os.path.join(base_dir, 'reports', 'figures/')
        # Source directory
        src_dir  = os.path.join(base_dir, 'src', 'data/')
        # Data path
        data_dir = os.path.join(base_dir, 'data/')
        # External path
        ext_dir  = os.path.join(data_dir, 'external/')
        # Processed path
        proc_dir = os.path.join(data_dir, 'processed/')
        # External path
        int_dir  = os.path.join(data_dir, 'interim/')
        # External path
        raw_dir  = os.path.join(data_dir, 'raw/')
        # Creating files
        for dir_ii in [plot_dir, src_dir, data_dir]:
            fd.Path_Folder(dir_ii)
        # Saving to dictionary
        param_dict = {}
        param_dict['base_dir'] = base_dir
        param_dict['plot_dir'] = plot_dir
        param_dict['src_dir' ] = src_dir
        param_dict['data_dir'] = data_dir
        param_dict['ext_dir' ] = ext_dir
        param_dict['proc_dir'] = proc_dir
        param_dict['int_dir' ] = int_dir
        param_dict['raw_dir' ] = raw_dir
    else:
        msg = '{0} `base_dir` ({1}) is not a Git directory! Exiting'.format(
            fd.Program_Msg(__file__), base_dir)
        raise LSSUtils_Error(msg)

    return param_dict

## Directory that holds code written in C-language
def get_code_c():
    """
    Path to the directory that holds scripts written in the C-language

    Returns
    ----------
    c_path : str
        Path to the directory with scripts written in C.
    """
    # Path Directory
    try:
        c_path = os.path.join(  os.getenv('HOME'),
                                'Codes2',
                                'custom_utilities_c/')
        assert(os.path.exists(c_path))
    except AssertionError:
        c_path = os.path.join(  os.getenv('HOME'),
                                'Codes',
                                'custom_utilities_c/')
        assert(os.path.exists(c_path))

    return c_path

## Directory for SDSS Catalogs
def get_sdss_catl_dir(path='./'):
    """
    Extracts the path to the set of SDSS catalogues

    Parameters
    ----------
    path : str, optional
        Path of the repository that would contain the set of SDSS catalogues.
        This path is only used if the environment variable `sdss_catl_path`
        is not available to the system.
        This variable is set to './' by default.

    Returns
    ----------
    catl_path : `str`
        Absolute path to the set of mock catalogues for SDSS.
    """
    ## Path to catalogues
    try:
        catl_path = os.environ['sdss_catl_path']
        assert(os.path.exists(catl_path))
    except:
        proj_dict = cookiecutter_paths(path)
        catl_path = proj_dict['base_dir']

    return catl_path

## Output directory for SDSS catalogues
def get_output_path():
    """
    Extracts path of SDSS catalogues within a directory

    Returns
    ----------
    path : str
        Path to the main output directory of the SDSS catalogues
    """
    # Reading in `output` path
    catl_path = get_sdss_catl_dir()
    # Main SDSS paths
    path = os.path.join(catl_path, 'data', 'external')
    assert(os.path.exists(path))

    return path
