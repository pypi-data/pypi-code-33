import ast

import numpy as np
import pandas as pd

from .messages import pack_to_dec


def _pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)

def read_simulation_log(filename):
    """Read a results file from a CustomSimulation.

    Parameters
    ----------
    filename : str
        File path or file object

    Returns
    -------
    results : dict
        Dict of all the results as returned from the original simulation.
    """
    with open(filename) as input_file:
        lines = input_file.readlines()
    sim_attr = lines.pop(0)
    enc_opt = ast.literal_eval(lines.pop(0))
    dec_opt = ast.literal_eval(lines.pop(0))
    mod_opt = ast.literal_eval(lines.pop(0))
    demod_opt = ast.literal_eval(lines.pop(0))
    test_opt = ast.literal_eval(lines.pop(0))
    results = {}
    for _key, _value in _pairwise(lines):
        key = ast.literal_eval(_key)
        value = ast.literal_eval(_value)
        results[key] = value
    return results

def read_hyperparameter_search_results(filename):
    """Read a results file from a HyperparameterSearchDecoderSimulation.

    Parameters
    ----------
    filename : str
        File path or file object

    Returns
    -------
    constants : dict
        Dict containing all the constants of the simulation.

    results : list
        List of all simulation results for the evaluated hyperparameter
        configurations.
    """
    with open(filename) as input_file:
        lines = input_file.readlines()
    constants = lines.pop(0)
    constants = ast.literal_eval(constants)
    results = []
    for _hyperparams, _results in _pairwise(lines):
        _hyperparams = ast.literal_eval(_hyperparams)
        _results = ast.literal_eval(_results)
        results.append((_hyperparams, _results))
    return constants, results

def read_codebook_file(filename, wiretap=False, columns=None, **kwargs):
    """Read a codebook file.

    Read a file which contains the codebook in columns.
    The default expected column names are `message` and `codeword`.

    Parameters
    ----------
    filename : str
        File path to the file.

    wiretap : bool, optional
        Set to True if the codebook is from a wiretap code.

    columns : dict, optional
        If provided, the entries are used as column names. The supported keys
        are `message`, `codeword`, and `random` for wiretap codes.

    **kwargs : keyword-arguments, optional
        All kwargs that can be passed to the pd.read_csv function.

    Returns
    -------
    codebook : dict
        Mapping of the messages to the codewords.
    
    code_info : dict
        Dict of different code parameters.
    """
    if columns is None:
        columns = {"codeword": "codeword", "message": "message",
                   "random": "random"}
    if 'sep' not in kwargs:
        kwargs['sep'] = '\t'
    data = pd.read_csv(filename, **kwargs)
    codebook = {}
    code_info = {}
    for idx, row in data.iterrows():
        message = ast.literal_eval(row[columns['message']])
        code_info['info_length'] = len(message)
        if wiretap:
            random = ast.literal_eval(row[columns['random']])
            code_info['random_length'] = len(random)
            message = message + random
        message = pack_to_dec([message])[0][0]
        codeword = ast.literal_eval(row[columns['codeword']])
        codebook[message] = codeword
        code_info['code_length'] = len(codeword)
    return codebook, code_info


def convert_codebook_to_dict(messages, codewords, random=None):
    """Convert a codebook representation to dictionary.

    Convert the codebook representation of multiple arrays to a single dict.

    Parameters
    ----------
    messages : array
        Array of the messages, where each row represents one message.

    codewords : array
        Array of the codewords corresponding to the messages.

    random : array, optional
        Optional array of random bits which is used for wiretap codes.

    Returns
    -------
    codebook : dict
        Codebook dictionary where the keys are the messages as decimal numbers.

    code_info : dict
        Dict of different code parameters.
    """
    codebook = {}
    code_info = {}
    code_info['info_length'] = np.shape(messages)[1]
    code_info['code_length'] = np.shape(codewords)[1]
    if random is not None:
        code_info['random_length'] = np.shape(random)[1]
        messages = np.hstack((messages, random))
    for message, codeword in zip(messages, codewords):
        message = pack_to_dec([message])[0][0]
        codebook[message] = codeword
    return codebook, code_info
