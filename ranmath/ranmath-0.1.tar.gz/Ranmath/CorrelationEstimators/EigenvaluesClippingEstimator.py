
from .AbstractEstimator import AbstractEstimator
from ..Resolvents import SimulatedEigenvaluesResolvent as resolvent
import numpy as np


class EigenvaluesClippingEstimator(AbstractEstimator):

    def __init__(self):
        super().__init__()

    def get_optimal_q(self, number_of_assets, number_of_samples):
        return number_of_assets / number_of_samples

    def estimate_eigenvalues(self, sample_estimator_eigenvalues,  q, verbose=False):

        n_iter, N = sample_estimator_eigenvalues.shape

        estimated_eigenvalues = np.zeros((n_iter, N))

        for it in range(n_iter):
            lambda_array = sample_estimator_eigenvalues[it]
            indexes_to_clip = []
            eigenvalues_to_clip = []

            for index in range(len(lambda_array)):
                if lambda_array[index] < (1 + np.sqrt(q)) ** 2:
                    indexes_to_clip.append(index)
                    eigenvalues_to_clip.append(lambda_array[index])

            clipped_value = np.array(eigenvalues_to_clip).mean()

            for index in indexes_to_clip:
                lambda_array[index] = clipped_value

            estimated_eigenvalues[it] = lambda_array

        return estimated_eigenvalues
