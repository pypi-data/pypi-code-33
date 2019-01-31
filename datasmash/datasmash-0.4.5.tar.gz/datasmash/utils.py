"""
Utility functions for data smashing including quantization and loading data
from the D3M format.
"""
import os
import json
import time
import csv
import warnings
import tempfile
import subprocess as sp
import numpy as np
import pandas as pd
from datasmash.config import BIN_PATH


def line_by_line(data_file, *, function, **kwargs):
    """

    """
    directory = os.path.dirname(os.path.realpath(data_file))
    tmp_dir = tempfile.mkdtemp(dir=directory)

    feature_file = data_file + '_features'
    with open(data_file, 'r') as infile:
        for i, line in enumerate(infile):
            line_file = os.path.join(tmp_dir, str(i))
            with open(line_file, 'w') as outfile:
                outfile.write(line)
            new_line_file = function(line_file, **kwargs)
            lines = []
            with open(new_line_file, 'r') as infile:
                for line_ in infile:
                    lines.append(line_)
            with open(feature_file, 'a+') as outfile:
                for line__ in lines:
                    outfile.write(line__)
    wait_for_file(feature_file)
    return feature_file


def genesess(data_file, *,
             outfile=None,
             multi_line=False,
             outfile_suffix='_',
             runfile=False,
             data_type='symbolic',
             data_direction='row',
             gen_epsilon=0.02,
             timer=False,
             data_length=1000000,
             num_steps=20000,
             num_models=1,
             featurization=True,
             depth=1000,
             verbose=False,
             bin_path=BIN_PATH):
    """

    """
    if not multi_line:
        gen_binary = [os.path.abspath(os.path.join(bin_path, 'genESeSS'))]
    else:
        gen_binary = [os.path.abspath(os.path.join(bin_path,
                                                   'genESeSS_feature'))]

    _data_file = ['-f', data_file]

    #if runfile:
    #    _outfile = []
    #    _runfile = ['-R', data_file + '_']
    #    _num_steps = ['-r', str(num_steps)]
    #    output = _runfile[1]
    #else:
    #    _outfile = ['-S', data_file + '_']
    #    _runfile = []
    #    _num_steps = []
    #    output = _outfile[1]

    if runfile:
        _outfile = ['-R']
        suffix = '_runfile'
        _num_steps = ['-r', str(num_steps)]
    else:
        _outfile = ['-S']
        suffix = '_features'
        _num_steps = []
    if outfile is None:
        _outfile.append(data_file + suffix)
    else:
        _outfile.append(outfile)
    output = _outfile[1]

    _data_type = ['-T', data_type]

    _data_direction = ['-D', data_direction]

    _gen_epsilon = ['-e', str(gen_epsilon)]

    _timer = ['-t', str(timer).lower()]

    _data_length = ['-x', str(data_length)]


    _num_models = ['-N', str(num_models)]

    if featurization:
        _featurization = ['-y', 'on']
    else:
        _featurizaiton = []

    _depth = ['-W', str(depth)]

    force_direction = ['-F']

    _verbose = ['-v']
    if verbose:
        _verbose.append("1")
    else:
        _verbose.append("0")

    command_list = (gen_binary
                    + _data_file
                    + _outfile
                    + _data_type
                    + _data_direction
                    + _gen_epsilon
                    + _timer
                    + _data_length
                    + _num_steps
                    + _num_models
                    + _featurization
                    + _depth
                    + force_direction
                    + _verbose)

    sp.run(command_list, encoding='utf-8')

    #print(command_list)
    #for f in os.listdir(os.path.dirname(os.path.realpath(_data_file[1]))):
    #    print(f)
    #wait_for_file(output)
    if not os.path.isfile(output):
        print('GenESeSS failed to run! Retrying...')
        return genesess(data_file, outfile=outfile, multi_line=multi_line,
                        outfile_suffix=outfile_suffix, runfile=runfile,
                        data_type=data_type, data_direction=data_direction,
                        gen_epsilon=gen_epsilon, timer=timer,
                        num_steps=num_steps, num_models=num_models,
                        featurization=featurization, depth=depth,
                        verbose=verbose, bin_path=bin_path)
    return output


def genesess_libfile(lib_file, *, alphabet_size, replace=True, **kwargs):
    """

    """
    if alphabet_size == 2:
        depth = 100
    elif alphabet_size >= 2:
        depth = 2000
    runfile_path = genesess(lib_file, depth=depth, **kwargs)
    return runfile_path
    #os.rename(runfile_path, lib_file)


def xgenesess(data_file, *,
              outfile=None,
              data_type='symbolic',
              num_lines='all',
              partition=None,
              detrending=None,
              min_delay=0,
              max_delay=30,
              bin_path=BIN_PATH):
    """

    """
    xgen_binary = [os.path.abspath(os.path.join(bin_path, 'XgenESeSS'))]

    _data_file = ['-f', data_file]

    _data_type = ['-T', data_type]

    _outfile = ['-Y']
    if outfile is None:
        _outfile.append(data_file + '_')
    else:
        _outfile.append(outfile)

    if num_lines == 'all':
        with open(data_file) as infile:
            _num_lines = sum(1 for _ in infile)
        _num_lines = num_lines_arg(_num_lines)
    #elif num_lines == 'one':
    else:
        _num_lines = "'0:0'"
    _selector = ['-k', _num_lines]

    if partition is None:
        _partition = []
    elif isinstance(partition, int):
        _partition = ['-p', str(partition)]
    elif isinstance(partition, list):
        _partition = ['-p'] + [str(p) for p in partition]

    if detrending is None:
        _detrending = []
    else:
        _detrending = ['-u', str(detrending)]

    _min_delay = ['-B', str(min_delay)]
    _max_delay = ['-E', str(max_delay)]

    _infer_model = ['-S']
    _print_gamma = ['-y', '1']
    _no_loading = ['-q']

    command_list = (xgen_binary
                    + _data_file
                    + _selector
                    + _data_type
                    + _partition
                    + _detrending
                    + _infer_model
                    + _min_delay
                    + _max_delay
                    + _print_gamma
                    + _outfile
                    + _no_loading)

    command_list = ' '.join(command_list)
    sp.run(command_list, shell=True)
    return _outfile[1]


def xgenesess_time(data_file, **kwargs):
    """

    """
    start = time.time()
    outfile = xgenesess(data_file, num_lines='one', **kwargs)
    end = time.time()
    elapsed_minutes = (end - start) / 60

    return elapsed_minutes


def serializer(bmp_filenames, *, outfile, bin_path=BIN_PATH, seq_len=1000,
               num_seqs=1, power_coeff=1.0, channel='R', size=16384,
               serializer_verbose=False):
    """

    """
    serializer_binary = [os.path.abspath(os.path.join(bin_path, 'serializer'))]
    _bmp_filenames = ['-f', bmp_filenames]
    _outfile = ['-o', outfile]
    _seq_len = ['-L', str(seq_len)]
    _num_seqs = ['-n', str(num_seqs)]
    _power_coeff = ['-w', str(power_coeff)]
    _channel = ['-c', channel]
    _size = ['-s', str(size)]
    _verbose = ['-v']
    if serializer_verbose:
        _verbose.append("1")
    else:
        _verbose.append("0")

    command_list = (serializer_binary
                    + _bmp_filenames
                    + _outfile
                    + _seq_len
                    + _num_seqs
                    + _power_coeff
                    + _channel
                    + _size
                    + _verbose)
    return sp.check_output(command_list, encoding='utf-8')


def smash(data_file, *,
          outfile='H.dst',
          partition=None,
          data_type='symbolic',
          data_direction='row',
          num_reruns=20,
          bin_path=BIN_PATH):
    """

    """
    smash_binary = [os.path.abspath(os.path.join(bin_path, 'smash'))]
    _data_file = ['-f', data_file]
    _outfile = ['-o', outfile]

    if partition is None:
        _partition = []
    elif type(partition) is int:
        _partition = ['-p', str(partition)]
    elif type(partition) is list:
        _partition = ['-p'] + [str(p) for p in partition]

    _data_type = ['-T', data_type]

    _data_direction = ['-D', data_direction]

    _num_reruns = ['-n', str(num_reruns)]

    command_list = (smash_binary
                    + _data_file
                    + _outfile
                    + _partition
                    + _data_type
                    + _data_direction
                    + _num_reruns)

    sp.check_output(command_list)
    results = np.loadtxt(outfile, dtype=float)
    results += results.T
    return results

def smashmatch(data_file, *,
               lib_files,
               output_prefix,
               partition=None,
               data_type='symbolic',
               data_direction='row',
               num_reruns=20,
               bin_path=BIN_PATH):
    """

    """
    smash_binary = [os.path.abspath(os.path.join(bin_path, 'smashmatch'))]
    _data_file = ['-f', data_file]
    _lib_files = ['-F'] + lib_files

    _outfile = ['-o', output_prefix]

    if partition is None:
        _partition = []
    elif type(partition) is int:
        _partition = ['-p', str(partition)]
    elif type(partition) is list:
        _partition = ['-p'] + [str(p) for p in partition]

    _data_type = ['-T', data_type]

    _data_direction = ['-D', data_direction]

    _num_reruns = ['-n', str(num_reruns)]

    command_list = (smash_binary
                    + _data_file
                    + _outfile
                    + _lib_files
                    + _partition
                    + _data_type
                    + _data_direction
                    + _num_reruns)

    sp.check_output(command_list)

    probs = pd.read_csv(output_prefix + '_prob', header=None, sep=' ')
    if probs.dropna(axis=1).shape[1] == 1:
        probs[1] = 0
        probs.to_csv(output_prefix + '_prob', sep=' ', header=False,
                     index=False)


def wait_for_file(new_file): # TODO: verbosity option
    """

    """
    if not os.path.exists(new_file):
        print('Beginning to wait for file: {}'.format(new_file))
        start = time.time()
        i = 0
        while not os.path.exists(new_file):
            time.sleep(1)
            i +=1
            if i % 30 == 0:
                end = time.time()
                elapsed = end - start
                print('Waiting for creation: {}'.format(new_file))
                print('Wait time thus far: {:.0f}'.format(elapsed))


def argmax_prod_matrix_list(matrix_list, *, index_class_map, axis=1):
    """

    """
    start = np.ones(matrix_list[0].shape)
    for matrix in matrix_list:
        start *= matrix
    argmaxes = np.argmax(start, axis=axis)
    if index_class_map:
        predictions = []
        for i in argmaxes:
            predictions.append(index_class_map[i])
        return predictions
    else:
        return argmaxes


def matrix_list_p_norm(matrix_list, *, p=2):
    """

    """
    matrix_list_power = np.array([np.power(matrix, p) for matrix in
                                  matrix_list])
    sum_ = np.sum(matrix_list_power, axis=0)
    norm = np.power(sum_, 1/p)
    return norm


def pprint_dict(dictionary, indent=False):
    """

    """
    for k, v in dictionary.items():
        if indent:
            indent = '\t'
        else:
            indent = ''
        print(indent + k + ':', v)
    print('\n')


def num_lines_arg(n):
    """

    """
    ratio_list = []
    for i in range(n):
        next_ratio = str(i) + ':' + str(i)
        ratio_list.append(next_ratio)
    ratio_string = ' | '.join(ratio_list)
    ratio_argument = str(repr(ratio_string))
    return ratio_argument

def predict_random(class_list, test_file):
    """

    """
    with open(test_file, 'r') as infile:
        num_predictions = sum(1 for _ in infile)
    random_predictions = np.random.choice(class_list,
                                          size=num_predictions)
    return random_predictions
