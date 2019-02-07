#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-02
# Last Modified: 2018-05-02
from __future__ import absolute_import, division, print_function
__author__     = ['Victor Calderon']
__copyright__  = ["Copyright 2018 Victor Calderon"]
__email__      = ['victor.calderon@vanderbilt.edu']
__maintainer__ = ['Victor Calderon']
__all__        = [  "Program_Msg",
                    "Index",
                    "get_immediate_subdirectories",
                    "Path_Folder",
                    "File_Exists",
                    "File_Download_needed",
                    "MarkParametrize"]
"""
Utilities for verifying file existence, directory paths, etc.
"""

## Import modules
import os
import subprocess
import time
import numpy as np
from   pathlib import Path
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

# Message for a filename. It displays the basename of the filename
def Program_Msg(filename):
    """
    Program message for `filename`

    Parameters
    ----------
    filename : string
        Path to the filename being used

    Returns
    ----------
    prog_msg : string
        String message for given `filename`
    """
    try:
        assert(os.path.exists(filename))
        # Creating message
        prog_msg = '\n\t\t==> {} >>> '.format(os.path.basename(filename))
    except:
        msg = '>>> `filename` {} not found! Exiting!'.format(filename)
        raise ValueError(msg)

    return prog_msg

## Compiles the array of files with matching pattern
def Index(pathdir, datatype, sort=True, basename=False):
    """
    Indexes the files in a directory `pathdir` with a specific data type
    `datatype`.

    Parameters
    ----------
    pathdir : string
        Path to the directory being analyzed

    datatype : string
        Type of documents to look for.

    sort : `bool`, optional (default = True)
        If this is set to True, the output list is sorted by name

    basename : `bool`, optional
        If this is set to True, the output list will contain only the
        basename of the files in `pathdir`

    Returns
    ----------
    file_arr : np.ndarray
        List of (sorted) files in `pathdir` with datatype `.datatype`
    """
    # Checking that directory exists
    if os.path.exists(pathdir):
        # List of files
        path_obj = Path(os.path.abspath(pathdir))
        file_arr = list(path_obj.rglob('*{0}'.format(datatype)))
        file_arr = np.array([x.as_posix() for x in file_arr])
        # Sorting
        if sort:
            file_arr = np.sort(file_arr)
        # Basenames
        if basename:
            file_arr = np.array([os.path.basename(x) for x in file_arr])
    else:
        msg = '{0} `pathdir` {1} not found!'.format(Program_Msg(__file__),
            pathdir)
        raise LSSUtils_Error(msg)

    return file_arr

## Immediate subdirectories for a given directory
def get_immediate_subdirectories(pathdir, sort=True):
    """
    Immediate subdirectories to a given directory path

    Parameters
    ----------
    pathdir : str
        Path to the desired directory

    Returns
    ----------
    subdir_arr : array_like or array of strings
        Array of paths of subdirectories of `pathdir`

    sort : `bool`, optional (default = True)
        If this is set to True, the output list is sorted by name
    """
    if os.path.exists(pathdir):
        path_obj = Path(pathdir)
        # List of subdirectories
        subdir_arr = np.array([x for x in os.listdir(pathdir)
                            if (os.path.isdir(str(path_obj.joinpath(x))) and
                                ('__' not in x))])
        if sort:
            subdir_arr = np.sort(subdir_arr)
    else:
        msg = '{0} `pathdir` {1} not found!'.format(Program_Msg(__file__),
            pathdir)
        raise LSSUtils_Error(msg)

    return subdir_arr

## Creates a Folder if needed
def Path_Folder(pathdir, time_sleep=0.5):
    """
    Creates a folder if it does not exist already

    Parameters
    ----------
    pathdir : str
        Path to the desired directory

    time_sleep : float, optional
        Amount of time in seconds to `sleep` or wait for the process to
        finish. By default `time_slee` is set to 0.5 seconds.
    """
    if os.path.exists(pathdir):
        pass
    else:
        while True:
            try:
                os.makedirs(pathdir)
                break
            except OSError as e:
                if e.errno != 17:
                    raise
                ## Adjusting time_sleep
                time.sleep(time_sleep)
                pass

## Checking if a file exists
def File_Exists(filename):
    """
    Detrmines if file exists or not

    Parameters
    -----------
    filename : str
        Absolute path to the file

    Raises
    -----------
    LSSUtils_Error : Exception
    """
    if os.path.exists(os.path.abspath(filename)):
        try:
            assert(os.path.isfile(os.path.abspath(filename)))
        except:
            msg = '{0} `filename` {1} not found!'.format(Program_Msg(__file__),
                filename)
            raise LSSUtils_Error(msg)
    else:
        msg = '{0} `filename` {1} not found!'.format(Program_Msg(__file__),
            filename)
        raise LSSUtils_Error(msg)

## Downloading a file from a remote server
def File_Download_needed(localpath, remotepath):
    """
    Determines if there exists a local copy of a file.
    If not, the file is downloaded from the remote server and a copy of
    the file is saved locally

    Parameters
    ----------
    localpath : str
        Local path to the file.

    remotepath : str
        Remote path to the file. This is the URL of the file, if there is
        no local copy of the file
    """
    file_msg = Program_Msg(__file__)
    # File extension - Remotely
    web_ext = os.path.splitext(remotepath)[1]
    # Checking if there is a local copy of the file
    if (os.path.exists(localpath) and os.path.isfile(localpath)):
        pass
    else:
        ## Downloading file
        # Testing for different kinds of files
        if web_ext == '.gz':
            cmd = 'wget {0} -O {0}{1}'.format(remotepath, localpath, web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
            # Unzipping file
            cmd = 'gzip -d {0}'.format(localpath + web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
        if web_ext == '.tar':
            cmd = 'wget {0} -O {0}{1}'.format(remotepath, localpath, web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
            # Unzipping file
            local_dir = os.path.dirname(localpath)
            cmd = 'tar zxf {0} - C {1}'.format(localpath + web_ext, local_dir)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
        else:
            cmd = 'wget {0} -O {1}'.format(remotepath, localpath)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
    ##
    ## Checking that file exists
    File_Exists(localpath)

## Parametrize set of inputs to a function
class MarkParametrize(object):
    """
    Parametrizes a set of values and changes the input variables
    of a function.
    """
    def __init__(self, argname, argvalues):
        """
        Initializes class object.

        Parameters
        ----------
        argname : `str`
            Key of the element to change in main dictionary.
            It can only contain 1 word at a time.

        argvalues : array-like
            List of argvalues for each of the `argnames`.
            This list will be used to loop over the values and
            replace them into the main dictionary.

        Notes
        ----------
        This function loops over the many different elements in `argvalues`.
        This function is meant to be used as a `decorator` for some
        function whose input a dictionary.
        """
        file_msg = fd.Program_Msg(__file__)
        ## Check input parameters
        # `argname`
        if not (isinstance(argname, str)):
            msg = '{0} `argname` ({1}) must be a string'.format(
                file_msg, type(argname))
            raise TypeError(msg)
        # `argvalues`
        if not (isinstance(argvalues, (tuple, list))):
            msg = '{0} `argvalues` ({1}) must be a tuple or list'.format(
                file_msg, type(argvalues))
            raise TypeError(msg)
        ## Assigning to class variables
        self.argname   = argname
        self.argvalues = argvalues
        self.file_msg  = file_msg
    ##
    ## Decorator
    def __call__(self, func):
        """
        This function gets executed when calling the function.
        This functions changes the value of arguments in `p_dict`, and
        runs the function `func` with the given parameters.

        Parameters
        ----------
        func : `function`
            Function that will be decorated.
        """
        def wrapped_func(*args, **kwargs):
            """
            This function changes the elements in `kwargs`
            """
            # Extracting main dictionary
            try:
                p_dict = kwargs['p_dict']
            except KeyError:
                try:
                    p_dict = args[0]
                except IndexError:
                    msg  = '{0} Could not read the input dictionary `p_dict`.'
                    msg += 'Please check your function!'
                    msg  = msg.format(self.file_msg)
                    raise LSSUtils_Error(msg)
            # Checking if `p_dict` is a dictionary
            if not (isinstance(p_dict, dict)):
                msg = '{0} `p_dict` must be a dictionary!'.format(
                    self.file_msg, type(p_dict))
                raise TypeError(msg)
            ## Parsing elements
            # `argvalues`
            argvalues = np.asarray(self.argvalues)
            ##
            ## Looping over elements
            for argval in argvalues:
                p_dict[self.argname] = argval
                func(p_dict=p_dict)

        return wrapped_func
