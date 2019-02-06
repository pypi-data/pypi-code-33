from .AbstractResolvent import AbstractResolvent
import numpy as np


class C1A1WishartResolvent(AbstractResolvent):
    def __init__(self):
        super().__init__()

    @staticmethod
    def compute(q, x_arr, eta, verbose=False):

        z_arr = np.array([complex(x, - eta) for x in x_arr])

        lambda_W_min = (1 - np.sqrt(q)) ** 2
        lambda_W_max = (1 + np.sqrt(q)) ** 2

        res_W_arr = (z_arr - 1 + q - np.sqrt(z_arr - lambda_W_min) * np.sqrt(z_arr - lambda_W_max)) / (2 * q * z_arr)

        return res_W_arr.real, np.abs(res_W_arr.imag)
