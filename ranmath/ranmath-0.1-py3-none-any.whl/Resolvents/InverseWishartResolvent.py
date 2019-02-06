from .AbstractResolvent import AbstractResolvent
import numpy as np


class InverseWishartResolvent(AbstractResolvent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def compute(q, kappa, x_arr, eta, verbose=False):

        z_arr = np.array([complex(x, - eta) for x in x_arr])

        lambda_Wishart_CIWA1_min = (1 + kappa * (1 + q) - np.sqrt((1 + 2 * kappa) * (1 + 2 * kappa * q))) / kappa
        lambda_Wishart_CIWA1_max = (1 + kappa * (1 + q) + np.sqrt((1 + 2 * kappa) * (1 + 2 * kappa * q))) / kappa

        res_Wishart_CIWA1_arr = (z_arr * (1 + kappa) + kappa * (q - 1) - kappa * np.sqrt(
            z_arr - lambda_Wishart_CIWA1_min) * np.sqrt(z_arr - lambda_Wishart_CIWA1_max)) / (
                                            z_arr * (2 * kappa * q + z_arr))

        return res_Wishart_CIWA1_arr.real, res_Wishart_CIWA1_arr.imag
