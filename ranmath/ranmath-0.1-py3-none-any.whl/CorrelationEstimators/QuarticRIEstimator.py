
from .AbstractEstimator import AbstractEstimator
from ..Resolvents import SimulatedEigenvaluesResolvent as resolvent
import numpy as np
from sympy import coth


class QuarticRIEstimator(AbstractEstimator):

    def __init__(self):
        super().__init__()

    def __quartic_equation(self, q, g, l, h, r):

        R0 = - l ** 2 * (h * l - 1) ** 2
        R1 = 4 * g * l * (h * l - 1) * q * (
        g ** 2 * q ** 2 * r ** 4 * l ** 4 - q ** 2 * r ** 4 * l ** 4 + g ** 2 * h ** 4 * q ** 2 * l ** 4 - h ** 4 * q ** 2 * l ** 4 + 2 * g ** 2 * h ** 2 * q ** 2 * r ** 2 * l ** 4 - 2 * h ** 2 * q ** 2 * r ** 2 * l ** 4 - 4 * g ** 2 * h ** 3 * q ** 2 * l ** 3 + 4 * h ** 3 * q ** 2 * l ** 3 - 4 * g ** 2 * h * q ** 2 * r ** 2 * l ** 3 + 4 * h * q ** 2 * r ** 2 * l ** 3 + h ** 2 * l ** 2 + 6 * g ** 2 * h ** 2 * q ** 2 * l ** 2 - 6 * h ** 2 * q ** 2 * l ** 2 + 2 * g ** 2 * q ** 2 * r ** 2 * l ** 2 - 2 * q ** 2 * r ** 2 * l ** 2 - r ** 2 * l ** 2 - 4 * g ** 2 * h * q ** 2 * l + 4 * h * q ** 2 * l - 2 * h * l + g ** 2 * q ** 2 - q ** 2 + 1)
        R2 = -(
        - g ** 2 * q ** 6 * r ** 8 * l ** 8 + q ** 6 * r ** 8 * l ** 8 - g ** 2 * h ** 8 * q ** 6 * l ** 8 + h ** 8 * q ** 6 * l ** 8 - 4 * g ** 2 * h ** 2 * q ** 6 * r ** 6 * l ** 8 + 4 * h ** 2 * q ** 6 * r ** 6 * l ** 8 - 6 * g ** 2 * h ** 4 * q ** 6 * r ** 4 * l ** 8 + 6 * h ** 4 * q ** 6 * r ** 4 * l ** 8 - 4 * g ** 2 * h ** 6 * q ** 6 * r ** 2 * l ** 8 + 4 * h ** 6 * q ** 6 * r ** 2 * l ** 8 + 8 * g ** 2 * h ** 7 * q ** 6 * l ** 7 - 8 * h ** 7 * q ** 6 * l ** 7 + 8 * g ** 2 * h * q ** 6 * r ** 6 * l ** 7 - 8 * h * q ** 6 * r ** 6 * l ** 7 + 24 * g ** 2 * h ** 3 * q ** 6 * r ** 4 * l ** 7 - 24 * h ** 3 * q ** 6 * r ** 4 * l ** 7 + 24 * g ** 2 * h ** 5 * q ** 6 * r ** 2 * l ** 7 - 24 * h ** 5 * q ** 6 * r ** 2 * l ** 7 - 28 * g ** 2 * h ** 6 * q ** 6 * l ** 6 + 28 * h ** 6 * q ** 6 * l ** 6 - 4 * g ** 2 * q ** 6 * r ** 6 * l ** 6 + 4 * q ** 6 * r ** 6 * l ** 6 - 2 * g ** 2 * q ** 4 * r ** 6 * l ** 6 + 3 * q ** 4 * r ** 6 * l ** 6 + 2 * g ** 2 * h ** 6 * q ** 4 * l ** 6 - 3 * h ** 6 * q ** 4 * l ** 6 - 36 * g ** 2 * h ** 2 * q ** 6 * r ** 4 * l ** 6 + 36 * h ** 2 * q ** 6 * r ** 4 * l ** 6 - 2 * g ** 2 * h ** 2 * q ** 4 * r ** 4 * l ** 6 + 3 * h ** 2 * q ** 4 * r ** 4 * l ** 6 - 60 * g ** 2 * h ** 4 * q ** 6 * r ** 2 * l ** 6 + 60 * h ** 4 * q ** 6 * r ** 2 * l ** 6 + 2 * g ** 2 * h ** 4 * q ** 4 * r ** 2 * l ** 6 - 3 * h ** 4 * q ** 4 * r ** 2 * l ** 6 + 56 * g ** 2 * h ** 5 * q ** 6 * l ** 5 - 56 * h ** 5 * q ** 6 * l ** 5 - 12 * g ** 2 * h ** 5 * q ** 4 * l ** 5 + 18 * h ** 5 * q ** 4 * l ** 5 + 24 * g ** 2 * h * q ** 6 * r ** 4 * l ** 5 - 24 * h * q ** 6 * r ** 4 * l ** 5 + 4 * g ** 2 * h * q ** 4 * r ** 4 * l ** 5 - 6 * h * q ** 4 * r ** 4 * l ** 5 + 80 * g ** 2 * h ** 3 * q ** 6 * r ** 2 * l ** 5 - 80 * h ** 3 * q ** 6 * r ** 2 * l ** 5 - 8 * g ** 2 * h ** 3 * q ** 4 * r ** 2 * l ** 5 + 12 * h ** 3 * q ** 4 * r ** 2 * l ** 5 - 70 * g ** 2 * h ** 4 * q ** 6 * l ** 4 + 70 * h ** 4 * q ** 6 * l ** 4 + 30 * g ** 2 * h ** 4 * q ** 4 * l ** 4 - 45 * h ** 4 * q ** 4 * l ** 4 - 6 * g ** 2 * q ** 6 * r ** 4 * l ** 4 + 6 * q ** 6 * r ** 4 * l ** 4 - 2 * g ** 2 * q ** 4 * r ** 4 * l ** 4 + 3 * q ** 4 * r ** 4 * l ** 4 - g ** 2 * q ** 2 * r ** 4 * l ** 4 + 3 * q ** 2 * r ** 4 * l ** 4 - g ** 2 * h ** 4 * q ** 2 * l ** 4 + 3 * h ** 4 * q ** 2 * l ** 4 - 60 * g ** 2 * h ** 2 * q ** 6 * r ** 2 * l ** 4 + 60 * h ** 2 * q ** 6 * r ** 2 * l ** 4 + 12 * g ** 2 * h ** 2 * q ** 4 * r ** 2 * l ** 4 - 18 * h ** 2 * q ** 4 * r ** 2 * l ** 4 - 18 * g ** 2 * h ** 2 * q ** 2 * r ** 2 * l ** 4 - 2 * h ** 2 * q ** 2 * r ** 2 * l ** 4 + 56 * g ** 2 * h ** 3 * q ** 6 * l ** 3 - 56 * h ** 3 * q ** 6 * l ** 3 - 40 * g ** 2 * h ** 3 * q ** 4 * l ** 3 + 60 * h ** 3 * q ** 4 * l ** 3 + 4 * g ** 2 * h ** 3 * q ** 2 * l ** 3 - 12 * h ** 3 * q ** 2 * l ** 3 + 24 * g ** 2 * h * q ** 6 * r ** 2 * l ** 3 - 24 * h * q ** 6 * r ** 2 * l ** 3 - 8 * g ** 2 * h * q ** 4 * r ** 2 * l ** 3 + 12 * h * q ** 4 * r ** 2 * l ** 3 + 36 * g ** 2 * h * q ** 2 * r ** 2 * l ** 3 + 4 * h * q ** 2 * r ** 2 * l ** 3 - 28 * g ** 2 * h ** 2 * q ** 6 * l ** 2 + 28 * h ** 2 * q ** 6 * l ** 2 + 30 * g ** 2 * h ** 2 * q ** 4 * l ** 2 - 45 * h ** 2 * q ** 4 * l ** 2 - h ** 2 * l ** 2 - 6 * g ** 2 * h ** 2 * q ** 2 * l ** 2 + 18 * h ** 2 * q ** 2 * l ** 2 - 4 * g ** 2 * q ** 6 * r ** 2 * l ** 2 + 4 * q ** 6 * r ** 2 * l ** 2 + 2 * g ** 2 * q ** 4 * r ** 2 * l ** 2 - 3 * q ** 4 * r ** 2 * l ** 2 - 18 * g ** 2 * q ** 2 * r ** 2 * l ** 2 - 2 * q ** 2 * r ** 2 * l ** 2 + r ** 2 * l ** 2 + 8 * g ** 2 * h * q ** 6 * l - 8 * h * q ** 6 * l - 12 * g ** 2 * h * q ** 4 * l + 18 * h * q ** 4 * l + 4 * g ** 2 * h * q ** 2 * l - 12 * h * q ** 2 * l + 2 * h * l - g ** 2 * q ** 6 + q ** 6 + 2 * g ** 2 * q ** 4 - 3 * q ** 4 - g ** 2 * q ** 2 + 3 * q ** 2 - 1)
        R3 = 8 * g * l * (h * l - 1) * q * r ** 2 * (
        h ** 2 * l ** 2 * q ** 2 + l ** 2 * r ** 2 * q ** 2 - 2 * h * l * q ** 2 + q ** 2 - 2 * h * l * q + 2 * q + 1) * (
             h ** 2 * l ** 2 * q ** 2 + l ** 2 * r ** 2 * q ** 2 - 2 * h * l * q ** 2 + q ** 2 + 2 * h * l * q - 2 * q + 1)
        R4 = r ** 2 * (
                      h ** 2 * l ** 2 * q ** 2 + l ** 2 * r ** 2 * q ** 2 - 2 * h * l * q ** 2 + q ** 2 - 2 * h * l * q + 2 * q + 1) ** 2 * (
                                                                                                                                            h ** 2 * l ** 2 * q ** 2 + l ** 2 * r ** 2 * q ** 2 - 2 * h * l * q ** 2 + q ** 2 + 2 * h * l * q - 2 * q + 1) ** 2
        quartic_equation = np.poly1d([R4, R3, R2, R1, R0])
        return quartic_equation

    def get_optimal_q(self, number_of_assets, number_of_samples):
        return number_of_assets / number_of_samples

    def get_optimal_eta(self, number_of_assets):
        return number_of_assets ** (-1/2)

    def estimate_eigenvalues(self, sample_est_eigenvalues_array, q, tau, eta=0.005, verbose=False):

        g = np.float64(coth(1 / tau))

        N = sample_est_eigenvalues_array.shape[0]

        quartic_eigenvalues = np.zeros(N)

        h_arr, r_arr = resolvent.compute_array(sample_est_eigenvalues_array, sample_est_eigenvalues_array, eta)

        for i in range(N):

            quartic_equation = self.__quartic_equation(q, g, sample_est_eigenvalues_array[i], h_arr[i], r_arr[i])

            quartic_roots = quartic_equation.r
            quartic_roots = quartic_roots[np.isreal(quartic_roots)]
            quartic_roots = quartic_roots[quartic_roots >= 0.]

            quartic_eigenvalues = quartic_roots[0].real

        return quartic_eigenvalues
