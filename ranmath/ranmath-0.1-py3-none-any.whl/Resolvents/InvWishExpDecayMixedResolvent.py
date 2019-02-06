from .AbstractResolvent import AbstractResolvent
import numpy as np
from sympy import coth


class InvWishExpDecayMixedResolvent(AbstractResolvent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def compute(q, kappa, tau, x_arr, verbose=False):

        b = np.exp(- 1. / tau)
        g = (1 + b ** 2) / (1 - b ** 2)

        res_Wishart_CIWAED_re_arr = []
        res_Wishart_CIWAED_im_arr = []

        for x in x_arr:

            G0 = (1 + 2 * kappa) ** 2
            G1 = - 4 * (1 + 2 * kappa) * (g * kappa * q + x + kappa * x)
            G2 = 2 * (
                        -2 * kappa ** 2 + 2 * kappa ** 2 * q ** 2 + 6 * g * kappa * q * x + 8 * g * kappa ** 2 * q * x + 3 * x ** 2 + 6 * kappa * x ** 2 + 2 * kappa ** 2 * x ** 2)
            G3 = - 4 * x * (
                        2 * kappa ** 2 * q ** 2 + 3 * g * kappa * q * x + 2 * g * kappa ** 2 * q * x + x ** 2 + kappa * x ** 2)
            G4 = x ** 2 * (4 * kappa ** 2 * q ** 2 + 4 * g * kappa * q * x + x ** 2)

            G_quartic_equation = np.poly1d([G4, G3, G2, G1, G0])

            G_quartic_roots = G_quartic_equation.r
            G_quartic_roots = G_quartic_roots[~np.isreal(G_quartic_roots)]

            if len(G_quartic_roots) == 2:
                res_Wishart_CIWAED_re_arr += [G_quartic_roots[0].real]
                res_Wishart_CIWAED_im_arr += [np.abs(G_quartic_roots[0].imag)]

        res_Wishart_CIWAED_re_arr = np.array(res_Wishart_CIWAED_re_arr)
        res_Wishart_CIWAED_im_arr = np.array(res_Wishart_CIWAED_im_arr)

        return res_Wishart_CIWAED_re_arr, np.abs(res_Wishart_CIWAED_im_arr)
