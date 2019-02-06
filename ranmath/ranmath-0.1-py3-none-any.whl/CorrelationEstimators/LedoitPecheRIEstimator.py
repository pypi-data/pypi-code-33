
from .AbstractEstimator import AbstractEstimator
from ..Resolvents import SimulatedEigenvaluesResolvent as resolvent
import numpy as np


class LedoitPecheRIEstimator(AbstractEstimator):

    def __init__(self):
        super().__init__()

    def get_optimal_q(self, number_of_assets, number_of_samples):
        return number_of_assets / number_of_samples

    def get_optimal_eta_scale(self, number_of_assets):
        return number_of_assets ** (-1/2)

    def estimate_eigenvalues(self, sample_estimator_eigenvalues, eta, q, verbose=False):

        n_iter, N = sample_estimator_eigenvalues.shape

        estimated_eigenvalues = np.zeros((n_iter, N))

        for it in range(n_iter):
            lambd = sample_estimator_eigenvalues[it]
            h, r = resolvent.compute_array(sample_estimator_eigenvalues, lambd, eta)
            H, R = q * (lambd * h - 1.), q * lambd * r
            estimated_eigenvalues[it] = lambd / ((H + 1.) ** 2 + R ** 2)

        return estimated_eigenvalues
