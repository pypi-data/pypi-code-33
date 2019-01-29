import numpy as np
import os


def load_data(data_file_name):

    module_path = os.path.dirname(__file__)
    data_path = os.path.join(module_path, 'data', data_file_name)
    
    data = np.load(data_path)
    
    return data

def load_example01():
    data = load_data('example01.npz')
    A = data['A']
    r = data['r']
    return A, r

def load_example02():
    data = load_data('example02.npz')
    A = data['A']
    r = data['r']
    return A, r

def load_example03():

    data_hex = load_data('example03hex.npz')
    data_sqr = load_data('example03sqr.npz')

    A_hex = data_hex['A']
    r_hex = data_hex['r']

    A_sqr = data_sqr['A']
    r_sqr = data_sqr['r']
    
    return A_hex, r_hex, A_sqr, r_sqr

def load_example03e44():

    data_hex = load_data('example03hex_e44.npz')
    data_sqr = load_data('example03sqr_e44.npz')

    res_hex = data_hex['res']
    res_sqr = data_sqr['res']

    return res_hex, res_sqr

def load_example04():

    data_norm = load_data('example04rNorm.npz')
    data_unif = load_data('example04rUnif.npz')

    A_norm = data_norm['A']
    r_norm = data_norm['r']

    A_unif = data_unif['A']
    r_unif = data_unif['r']
    
    return A_norm, r_norm, A_unif, r_unif
