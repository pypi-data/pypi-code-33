from .AbstractResolvent import AbstractResolvent
import numpy as np
from sympy import coth


class ExponentialDecayResolvent(AbstractResolvent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def compute(q, tau, x_arr, verbose=False):

        b = np.exp(- 1. / tau)
        g = (1 + b ** 2) / (1 - b ** 2)

        res_Wishart_C1AED_re_arr = []
        res_Wishart_C1AED_im_arr = []

        for x in x_arr:

            G0 = 1
            G1 = - 2 * (g * q + x)
            G2 = - 1 + q ** 2 + 4 * g * q * x + x ** 2
            G3 = - 2 * q * x * (q + g * x)
            G4 = q ** 2 * x ** 2

            G_quartic_equation = np.poly1d([G4, G3, G2, G1, G0])

            G_quartic_roots = G_quartic_equation.r
            G_quartic_roots = G_quartic_roots[~np.isreal(G_quartic_roots)]

            if len(G_quartic_roots) == 2:
                res_Wishart_C1AED_re_arr += [G_quartic_roots[0].real]
                res_Wishart_C1AED_im_arr += [np.abs(G_quartic_roots[0].imag)]

        res_Wishart_C1AED_re_arr = np.array(res_Wishart_C1AED_re_arr)
        res_Wishart_C1AED_im_arr = np.array(res_Wishart_C1AED_im_arr)

        return res_Wishart_C1AED_re_arr, np.abs(res_Wishart_C1AED_im_arr)
