'''
Provide the reflection matrix for vacuum fluctuations entering the input 
mirror, and the transmission matrix for vacuum fluctuations entering the 
end mirror, of ONE filter cavity. 

References:

MAGIC
@author: Isobel
'''
import magic.utils.transfer_functions.transfer_matrix as transfer_matrix
import magic.utils.transfer_functions.transfer_matrix_product as transfer_matrix_product
from magic import constants
import numpy as np


def calculate(f, p, rot, R_min, T_min=1):

    L_f = p['L_f']
    f_detune = p['f_detune']
    T_im = p['T_im']
    T_em = p['T_em']
    round_trip_loss = p['round_trip_loss']

    R_im = np.sqrt(1 - T_im)
    R_em = np.sqrt(1 - T_em)
    R_rm = R_im * R_em * np.sqrt(1 - round_trip_loss)

    # Phases for +/- audio sidebands
    w = 2 * np.pi * f
    w_f = 2 * np.pi * f_detune
    c = constants.c
    ephi_p = np.exp(1j * 2 * (w - w_f) * L_f / c)
    ephi_m = np.exp(1j * 2 * (-w - w_f) * L_f / c)

    # Cavity gains
    g_p = 1 / (1 - R_rm * ephi_p)
    g_m = 1 / (1 - R_rm * ephi_m)

    # Reflectivity of vacuum fluctuation, input mirror entrance
    R_p = R_im - R_em * T_im * ephi_p * g_p
    R_m = R_im - R_em * T_im * ephi_m * g_m

    # Transmissivity of vacuum fluctuation, end mirror entrance
    T_p = np.sqrt(T_im * T_em * ephi_p) * g_p
    T_m = np.sqrt(T_im * T_em * ephi_m) * g_m

    # Transmissivity of vacuum fluctuation, losses in cavity
    L_p = np.sqrt(T_im * round_trip_loss * ephi_p) * g_p
    L_m = np.sqrt(T_im * round_trip_loss * ephi_m) * g_m

    # Reflection matrix, input mirror (a+, (a-)* basis)
    M_r_0 = transfer_matrix.calculate(R_p, 0, 0, np.conj(R_m))
    # Transmission matrix, end mirror
    M_t_0 = transfer_matrix.calculate(T_p, 0, 0, np.conj(T_m))
    # Transmission matrix, losses
    M_l_0 = transfer_matrix.calculate(L_p, 0, 0, np.conj(L_m))

    # Change-of-basis matrix to a+ and (a-)*
    M_cob = np.array([[1, 1j], [1, -1j]])
    M_r = transfer_matrix_product.calculate(M_r_0, M_cob)
    M_t = transfer_matrix_product.calculate(M_t_0, M_cob)
    M_l = transfer_matrix_product.calculate(M_l_0, M_cob)

    M_cob = np.linalg.inv(M_cob)

    M_R = transfer_matrix_product.calculate(M_cob, M_r)
    M_T = transfer_matrix_product.calculate(M_cob, M_t)
    M_L = transfer_matrix_product.calculate(M_cob, M_l)

    # Reflected fields
    if R_min == []:
        M_n = np.zeros((2, 0, f.size))
    else:
        if np.isscalar(R_min):
            M_n = M_R * R_min
        else:
            M_n = transfer_matrix_product.calculate(M_R, R_min)

    # Transmitted fields
    if T_min != [] and T_em > 0:
        if np.isscalar(T_min) and T_min == 1:
            M_n = np.hstack(M_n, M_T)
        else:
            M_n = np.hstack((M_n, transfer_matrix_product.calculate(M_T, T_min)))

    # Loss fields
    if round_trip_loss > 0:
        M_n = np.hstack((M_n, M_L))

    return M_R, M_T, M_n
