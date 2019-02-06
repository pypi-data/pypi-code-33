
from .AbstractResolvent import AbstractResolvent
import numpy as np


class SimulatedEigenvaluesResolvent(AbstractResolvent):

    def __init__(self):
        super().__init__()

    @staticmethod
    def compute(eigenvalues_array, x, eta, verbose=False):

        result = (1 / (complex(x, - eta) - eigenvalues_array)).mean()
        return result.real, result.imag

    @staticmethod
    def compute_array(eigenvalues_array, x_array, eta, verbose=False):

        real_list = []
        imaginary_list = []

        for x in x_array:
            real, imaginary = SimulatedEigenvaluesResolvent.compute(eigenvalues_array, x, eta)
            real_list += [real]
            imaginary_list += [imaginary]

        return np.array(real_list), np.array(imaginary_list)

