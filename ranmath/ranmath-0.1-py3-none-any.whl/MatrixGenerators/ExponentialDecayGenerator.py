
from .AbstractGenerator import AbstractGenerator
from .MultivariateGaussianGenerator import MultivariateGaussianGenerator
import numpy as np


class ExponentialDecayGenerator(AbstractGenerator):

    def __init__(self, number_of_assets, number_of_samples, autocorrelation_time, number_of_iterations):
        super().__init__()
        self.__number_of_assets = number_of_assets
        self.__number_of_samples = number_of_samples
        self.__autocorrelation_time = autocorrelation_time
        self.__number_of_iterations = number_of_iterations
        self.__last_C = None
        self.__last_A = None

    @property
    def last_C(self):
        return self.__last_C

    @property
    def last_A(self):
        return self.__last_A

    def generate(self, verbose=False):

        if verbose:
            print("Generating using Exponential Decay")

        N, T = self.__number_of_assets, self.__number_of_samples

        A = np.array(
            [[np.exp(-np.abs(a - b) / self.__autocorrelation_time) for b in range(T)] for a in range(T)]
        )

        self.__last_C = np.eye(N)
        self.__last_A = A

        mv_generator = MultivariateGaussianGenerator(np.eye(N), A, self.__number_of_iterations)

        return mv_generator.generate(verbose=verbose)
