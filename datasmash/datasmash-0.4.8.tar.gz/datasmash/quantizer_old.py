"""
Quantizer class and functions.
"""
import os
import csv
import tempfile
import subprocess as sp
from shutil import copyfile
import numpy as np
import pandas as pd
from datasmash.config import BIN_PATH
from datasmash.utils import genesess_libfile



def detrend(df, *, detrend_level):
    """

    """
    return df.diff(axis=1).dropna(how='all', axis=1)


def detrend_old(df, *, detrend_level):
    """

    """
    length = len(df.columns)
    detrended_list = []
    for _, row_ in df.iterrows():
        row = pd.DataFrame(row_).transpose()
        shifted_row = []
        row.dropna(axis=1, inplace=True)
        for i in range(detrend_level + 1):
            end = length - detrend_level + i
            next_ = row.iloc[:, i:end]
            next_.columns = range(next_.shape[1])
            shifted_row = [next_] + shifted_row
        detrended_row = shifted_row[0] - sum(shifted_row[1:])
        detrended_list.append(detrended_row)
    detrended_df = pd.DataFrame(detrended_list)
    return detrended_df


def normalize(df):
    """

    """
    standard_normal_rows = df.subtract(df.mean(axis=1),
                                       axis=0).divide(df.std(axis=1), axis=0)
    return standard_normal_rows


def prune(df, lower_bound, upper_bound):
    """

    """
    for index in df.index:
        X = []
        for val in df.iloc[index].values:
            if val <= lower_bound or val >= upper_bound:
                X = np.append(X,val)
        pruned_ = np.empty([1, len(df.iloc[index].values) - len(X)])
        pruned_[:] = np.nan
        X = np.append(X, pruned_)
        df.loc[index] = X
    return df


def quantize_inplace(filename, *, partition, pruning=None, detrending=None,
                     normalization=None, outfile=None, verbose=False):
    """

    """
    max_col_len = 0
    with open(filename, 'r') as infile:
        csv_reader = csv.reader(infile, delimiter=' ')
        for row in csv_reader:
            len_ = len(row)
            if len_ > max_col_len:
                max_col_len = len_
    unquantized = pd.read_csv(filename, delimiter=' ', dtype='float',
                              header=None, names=range(max_col_len))

    if pruning:
        if verbose:
            print('PRUNING')
        unquantized = prune(unquantized, pruning[0], pruning[1])
    if detrending:
        if verbose:
            print('DETRENDING')
        unquantized = detrend(unquantized, detrend_level=detrending)
    if normalization:
        if verbose:
            print('NORMALIZING')
        unquantized = normalize(unquantized)

    if outfile is None:
        _outfile = filename
    else:
        _outfile = outfile
        #filename_split = os.path.splitext(filename)
        #_outfile = filename_split[0] + outfile_suffix + filename_split[1]
    quantized = np.digitize(unquantized, bins=partition)
    np.savetxt(_outfile, quantized, fmt='%d', delimiter=' ')


def read_quantizer_params(parameters):
    """

    """
    prune_range = []
    for index, char in enumerate(parameters):
        if char == 'R':
            for char_ in parameters[index+2:]:
                if char_ != ']':
                    prune_range.append(char_)
                else:
                    break
        elif char == 'D':
            detrending = int(parameters[index+1])
        elif char == 'N':
            normalization = int(parameters[index+1])
    if prune_range:
        prune_range = ''.join(prune_range).split(' ')
    partition = parameters.split('[')[-1].strip(']').split()

    return prune_range, detrending, normalization, partition


def write_quantizer_params(prune_range, detrending, normalization, partition):
    """

    """
    params = []
    if prune_range:
        params.append('R')
        params += prune_range
    if detrending:
        params.append('D')
        params.append(detrending)
    if normalization:
        params.append('N')
        params.append(normalization)
    if partition:
        params.append('P')
        params += partition
    params_string = ''.join([str(p) for p in params])
    return params_string


def quantizer(data_dir, *, problem_type,
              num_streams=-1,
              sample_size=0.5,
              bin_path=BIN_PATH,
              pooled=True,
              epsilon=-1,
              min_alphabet_size=2,
              max_alphabet_size=3,
              use_genesess=True,
              gen_epsilon=0.02,
              num_steps=20000,
              num_models=1,
              partition=None,
              detrending=None,
              normalization=None,
              runfile=False,
              multi_partition=False,
              verbose=False):
    """
    use_genesess=True only for GSmashClassification()
    """
    _problem_type = ['-t']
    _num_streams = ['-T']
    if problem_type == 2 or problem_type == 'supervised':
        _problem_type.append("2")
        _num_streams.append("-1")
    else:
        assert num_streams > 0, ("a positive number must be specified for "
                                 "total number of streams")
        _num_streams.append(str(num_streams))
        if problem_type == 1 or problem_type == 'unsupervised_with_targets':
            _problem_type.append("1")
        elif problem_type == 0 or problem_type == 'unsupervised':
            _problem_type.append("0")

    if partition is None:
        quantizer_binary = [os.path.abspath(os.path.join(bin_path, 'Quantizer'))]
        _data_dir = ['-D', data_dir]

        _sample_size = ['-x', str(sample_size)]

        _pooled = ['-w']
        if pooled:
            _pooled.append("1")
        else:
            _pooled.append("0")

        _epsilon = ['-e', str(epsilon)]

        _min_alphabet_size = ['-a', str(min_alphabet_size)]
        _max_alphabet_size = ['-A', str(max_alphabet_size)]

        if detrending is not None:
            _detrending = ['-d', str(detrending)]
        else:
            _detrending = []

        if normalization is not None:
            _normalization = ['-n', str(int(normalization))]
        else:
            _normalization = []

        command_list = (quantizer_binary +
                        _data_dir +
                        _problem_type +
                        _num_streams +
                        _sample_size +
                        _pooled +
                        _epsilon +
                        _min_alphabet_size +
                        _max_alphabet_size +
                        _detrending +
                        _normalization)
        raw_output = sp.check_output(command_list, encoding='utf-8')

        if not multi_partition:
            parameters = raw_output.strip().split('\n')[-1]
            prune_range, detrending, normalization, partition = read_quantizer_params(parameters)
            prune_range_list = [prune_range]
            detrending_list = [detrending]
            normalization_list = [normalization]
            partition_list = [partition]
        else:
            prune_range_list = []
            detrending_list = []
            normalization_list = []
            partition_list = []

            valid_params_path = os.path.join(data_dir, 'valid_parameters')
            parameters = open(valid_params_path).read().splitlines()
            for param in parameters:
                pr, d, n, pa = read_quantizer_params(param)
                prune_range_list.append(pr)
                detrending_list.append(d)
                normalization_list.append(n)
                partition_list.append(pa)
            prune_range = prune_range_list[0]
            detrending = detrending_list[0]
            normalization = normalization_list[0]
            partition = partition_list[0]

    lib_list_path = os.path.join(data_dir, 'library_list')
    lib_list = []
    if _problem_type[1] == "2":
        with open(lib_list_path, 'r') as infile:
            for line in infile:
                train_metadata = line.strip().split(' ')
                lib_file = train_metadata[0]
                lib_list.append(lib_file)
    else:
        lib_list.append('dataset')

    qdata_dir = os.path.join(data_dir, 'quantized_data')
    os.mkdir(qdata_dir)

    qlib_dir_list = []
    params = zip(prune_range_list, detrending_list, normalization_list,
                 partition_list)

    q_order = []
    parameter_dict_list = []
    for i, (pr, d, n, pa) in enumerate(params):
        suffix = write_quantizer_params(pr, d, n, pa)
        for lib_file in lib_list:
            lib_name = os.path.splitext(lib_file)[0]
            lib_file_path = os.path.join(data_dir, lib_file)
            qlib_dir = os.path.join(qdata_dir, lib_name)
            qlib_dir_list.append(qlib_dir)
            qlib_name = lib_name + '_' + suffix
            qlib_path = os.path.join(qlib_dir, qlib_name)
            quantize_inplace(lib_file_path, outfile=qlib_path,
                             partition=pa, pruning=pr, detrending=d,
                             normalization=n)
            if use_genesess:
                alphabet_size = len(pa) + 1
                genesess_libfile(lib_file_path, alphabet_size,
                                 gen_epsilon=gen_epsilon,
                                 num_steps=num_steps,
                                 num_models=num_models,
                                 runfile=runfile)

        q_order.append(suffix)
        parameter_dict = {'prune_range': pr,
                          'detrending': d,
                          'normalization': n,
                          'partition': pa}
        parameter_dict_list.append(parameter_dict)

    return q_order, parameter_dict_list, qlib_dir_list


