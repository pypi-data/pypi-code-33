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
__all__        = [  "IDL_read_file",
                    "fast_food_reader",
                    "read_pandas_hdf5",
                    "read_hdf5_file_to_pandas_DF",
                    "pandas_file_to_hdf5_file",
                    "pandas_df_to_hdf5_file",
                    "concatenate_pd_df"]
"""
Set of functions to read various types of files
"""

# Import modules
import struct
import os
import sys
import numpy as np
import pandas as pd
import h5py
from   scipy.io.idl import readsav
from   cosmo_utils.utils import file_utils as fd
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

# Reads in IDL catalogue as Python dictionary
def IDL_read_file(idl_file):
    """
    Reads an IDL file and converts it to a Python dictionary

    Parameters
    ----------
    idl_file : string
        Path to the filename being used

    Returns
    ----------
    idl_dict : python dictionary
        Dictionary with the data from `idl_file`
    """
    # Checking that file exists
    fd.File_Exists(idl_file)
    # Converting to dictionary
    try:
        idl_dict = readsav(idl_file, python_dict=True)
    except:
        msg = '{0} `idl_file` {0} is not an IDL file'.format(
            fd.Program_Msg(__file__), idl_file)
        raise LSSUtils_Error(msg)

    return idl_dict

# Reads in `fastfood`-type files and converts it to an array
def fast_food_reader(key, nitems, filename):
    """
    Reads in `fastfood`-type file and converts it to an array

    Parameters
    ----------
    key : {'int', 'float', 'double', 'long'}, str
        Type of the element to extract.

    nitmes : int
        Number of items to expect and exctract.

    filename : str
        Absolute path to the file, from which to extract the information.

    Returns
    ----------
    items_arr : np.ndarray, shape (`nitems`,)
        Array of elements from `filename` with length `nitems`.
    """
    # Dictionaries with values for `key`
    size_types  = { 'int'       :4  , 'float'       :4   , 'char'    :1 ,\
                    'short_int' :2  , 'long_int'    :4   , 'bool'    :1 ,\
                    'double'    :8  , 'long_double' :8   , 'wchart_t':2 }
    ##
    type_string = { 'char'         :'c', 'signed_char'       :'b',\
                    'unsigned_char':'B', '_Bool'             :'?',\
                    'short'        :'h', 'unsigned_short'    :'H',\
                    'int'          :'i', 'unsigned_int'      :'I',\
                    'long'         :'l', 'unsigned_long'     :'L',\
                    'long_long'    :'q', 'unsigned_long_long':'Q',\
                    'float'        :'f', 'double'            :'d' }
    ## Defining types and sizes
    if key == 'int':
        size_type = size_types ['int']
        type_str  = type_string['int']
    if key == 'float':
        size_type = size_types ['float']
        type_str  = type_string['float']
    if key == 'long':
        size_type = size_types ['long_double']
        type_str  = type_string['long']
    if key == 'double':
        size_type = size_types ['double']
        type_str  = type_string['double']
    ##
    # Top padding (it should contain 4 bytes for `.ff` files)
    # 1st padding = nbyte1
    nbyte1_read = filename.read(1 * size_types['int'])
    nbyte1      = struct.unpack(1 * type_string['int'], nbyte1_read)
    nbyte1_val  = int(nbyte1[0])
    if len(nbyte1) != 1:
        errno = -10
        raise ValueError('Read error: file empty?. \nError: ' + str(errno))
        sys.exit()
    # Extracting data
    nitem1_read = filename.read(size_type * nitems)
    items_arr     = struct.unpack(type_str * nitems, nitem1_read)
    val_len     = len(items_arr)
    if val_len != nitems:
        errno = -20
        raise ValueError('Read Error: {0} items expected. Read {1}'.format(
            nitems, val_len))
        sys.exit()
    # Bottom padding
    nbyte2_read = filename.read(size_types['int'])
    nbyte2      = struct.unpack(1 * type_string['int'], nbyte2_read)
    nbyte2_val  = int(nbyte2[0])
    if len(nbyte2) != 1:
        errno = -30
        raise ValueError('Read Error: File too short?\n Errno: ' + str(errno))
        sys.exit()
    # Checking top and bottom
    if nbyte1_val != nbyte2_val:
        errno = -1
        Err_msg = 'Read warning. Byte numbers do not match \n '
        Err_msg += 'nbyte1 = {0}, nbyte2 = {1}\n'.format(nbyte1, nbyte2)
        raise ValueError(Err_msg + 'Errno: {0}'.format(errno))
        sys.exit()
    # Checking that nbye1_val = nitems*Size_type[key]
    if nbyte1_val != nitems * size_type:
        errno = -2
        Err_msg = 'Read warning. Byte numbers do not match \n '
        Err_msg += 'nbyte1 = {0}, nitems = {1}\n'.format(nbyte1, nitems)
        raise ValueError(Err_msg + 'Errno: {0}'.format(errno))
        sys.exit()
    #
    # Converting values to numpy array
    items_arr = np.asarray(items_arr)

    return items_arr

# Reads in a pandas DataFrame from a HDF5 file
def read_pandas_hdf5(hdf5_file, key=None, ret=False):
    """
    Reads a HDF5 file that contains one or many datasets.
    It converts it into a pandas DataFrame.

    Parameters
    ----------
    hdf5_file : str
        Path to the HDF5 file containing one or more pandas DataFrame(s).

    key : str or NoneType
        If provided, it will extract the `key` value as a pandas DataFrame.
        This value is set to `None` by default.

    ret : `bool`, optional
        If True, it returns the value of the `key`.
        By default, it is set to False.

    Returns
    ----------
    df : `pandas.DataFrame`
        DataFrame from the `hdf5_file` with the data from the `key` directory
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking that file exists
    fd.File_Exists(hdf5_file)
    # Checking number of keys
    hdf5_obj  = pd.HDFStore(hdf5_file)
    hdf5_keys = [ii for ii in hdf5_obj.keys()]
    hdf5_obj.close()
    # Reading in HDF5 file
    if key is None:
        try:
            df = pd.read_hdf(hdf5_file)
            if ret:
                return df, hdf5_keys[0]
            else:
                return df
        except:
            msg  = '{0} Must specify which key to use:\n\t'.format(file_msg)
            msg += 'Possible keys: \n'
            print(msg)
            for key_i, name in enumerate(hdf5_keys):
                print('\t Key {0}:  {1}'.format(key_i, name))
    else:
        if key not in hdf5_keys:
            print('{0} Key not in the file: '.format(file_msg))
            print('Possible Keys:\n')
            for key_i, name in enumerate(hdf5_keys):
                print('\t Key {0}:  {1}'.format(key_i, name))
        else:
            df = pd.read_hdf(hdf5_file, key=key)
            if ret:
                return df, key
            else:
                return df

# Reads HDF5 files and converts them to pandas dataframe
def read_hdf5_file_to_pandas_DF(hdf5_file, key=None):
    """
    Reads content of HDF5 file and converts it to a Pandas DataFrame

    Parameters
    ----------
    hdf5_file : str
        Path to the HDF5 file. This is the file that will be converted
        to a pandas DataFrame.

    key : str or NoneType, optional
        Key or path in `hdf5_file` for the pandas DataFrame and the normal
        HDF5 file.

    Returns
    ----------
    df : `pandas.DataFrame`
        DataFrame from `hdf5_file` under the `key` directory.
    """
    file_msg = fd.Program_Msg(__file__)
    fd.File_Exists(hdf5_file)
    # Reading in Pandas DataFrame
    try:
        df = pd.read_hdf(hdf5_file, key=key)
    except:
        msg = '{0} Could not read `hdf5_file` ({1})! Please check if it exists'
        msg = msg.format(file_msg, hdf5_file)
        raise LSSUtils_Error(file_msg)

    return df

# Converts pandas DataFrame to HDF5 file format
def pandas_file_to_hdf5_file(df_file, hdf5_file, key=None, mode='w'):
    """
    Converts a HDF5 with pandas format and converts it to normal HDF5 file

    Paramters
    ---------
    df_file : str
        Path to the `df_file` containing the pandas DataFrame to be converted

    hdf5_file : str
        Path to the output HDF5 file containg arrays as keys

    key : str or NoneType, optional
        Key or path in HDF5 file for the `df_file` and `hdf5_file`
    """
    file_msg = fd.Program_Msg(__file__)
    fd.File_Exists(df_file)
    # Reading in DataFrame
    if not key:
        data, key = read_pandas_hdf5(df_file, key=None, ret=True)
    else:
        data = read_pandas_hdf5(df_file, key=key)
    # Rearranging data
    arr_names   = data.dtypes.index.values
    dtypes_arr  = data.dtypes.values
    dtypes_arr  = np.array([x.str for x in dtypes_arr])
    data_dtypes = np.dtype(zip(arr_names, dtypes_arr))
    dataset     = np.recarray((len(data),), dtype=data_dtypes)
    for name in dataset.dtype.names:
        dataset[name] = data[name]
    # Saving file to HDF5 format
    hdf5_obj = h5py.File(hdf5_file, mode=mode)
    hdf5_obj.create_dataset(key, data=dataset)
    hdf5_obj.close()
    msg = '{0} HDF5 file created: {1}'.format(file_msg, hdf5_file)
    print(msg)

# Saves a pandas DataFrame into a normal or a `pandas` HDF5 file
def pandas_df_to_hdf5_file(df, hdf5_file, key=None, mode='w', complevel=8):
    """
    Saves a `pandas.DataFrame` into a `pandas` HDF5 FILE.

    Parameters
    ----------
    df : `pandas.DataFrame`
        DataFrame to be converted and saved into a HDF5 file.

    hdf5_file : str
        Path to the output HDF5 file

    key : str or NoneType, optional
        Key or path, under which `df` will be saved in the `hdf5_file`.

    mode : {'w','a'}, optional
        Mode to handle `hdf5_file`. This value is set to `w` by default,
        which stand for `write`.

    complevel : int, optional
        Level of compression for `hdf5_file`.
        The range of `complevel` is rane(0-9).
        This is set to a default of 8.
    """
    file_msg = fd.Program_Msg(__file__)
    # Saving DataFrame to `hdf5_file`
    try:
        df.to_hdf(hdf5_file, key, mode=mode, complevel=complevel)
        msg = '{0} HDF5 file created: {1}'.format(file_msg, hdf5_file)
        print(msg)
    except:
        msg = '{0} Could not create HDF5 file'.format(file_msg)
        raise LSSUtils_Error(msg)

# Concatenating pandas DataFrame into a single DataFrame
def concatenate_pd_df(directory, filetype='hdf5', foutput=None, outonly=True):
    """
    Concatenates pandas DataFrames into a single DataFrame

    Parameters
    ----------
    directory : str
        Path to the folder containing multiple pandas-HDF5 files

    filetype : str, optional
        File format of the file in `directory` to be read
        This is set to `hdf5` by default.

    foutput : str or NoneType
        If not `None`, it is the basename of the output file in HDF5 format

    outonly : `bool`, optional
        If True, it returns the pandas DataFrame.
        If False, it only saved the concatenated `pandas.DataFrame`.

    Returns
    ----------
    df_conc : `pandas.DataFrame`
        DataFrame containing the combined datasets from the files in
        `directory`.

    Raises
    ----------
    LSSUtils_Error : Exception
        If no files are found in `directory`, it raises an error
        warning about this.
    """
    file_msg = fd.Program_Msg(__file__)
    # Checking that `directory` exists
    if not os.path.exists(directory):
        msg = '{0} `directory` {1} is not a valid path! Exiting!'.format(
            file_msg, directory)
        raise LSSUtils_Error(msg)
    # Concatenating files
    files_arr = fd.index(directory, '.' + filetype, sort=True)
    print('{0} Found `{1}` files'.format(file_msg, files_arr.size))
    if len(files_arr) > 0:
        # Initializing array that contains info
        df_arr = [[] for x in range(len(files_arr))]
        # Looping over HDF5 (pandas) files
        for ii, file_ii in enumerate(files_arr):
            df_arr[ii] = read_pandas_hdf5(file_ii)
        # Concatenating arrays
        df_conc = pd.concat(df_arr, ignore_index=True)
        # Deciding name of resulting output file
        if (foutput is not None) and (type(foutput) == str):
            foutput_file = os.path.join(directory,
                                        '{0}.{1}'.format(foutput, filetype))
            # Saving resulting DataFrame
            pandas_df_to_hdf5_file(df_conc, foutput_file, key='/Main')
            # Checking file exists
            fd.File_Exists(foutput_file)
            print('{0} Output file saved in: {2}'.format(
                file_msg, foutput_file))
        # If only outputting concatenated DataFrame
        if outonly:
            return df_conc
    else:
        msg = '{0} No files in `{1}` with extension `{2}`'.format(file_msg,
                directory, filetype)
        raise LSSUtils_Error(msg)
