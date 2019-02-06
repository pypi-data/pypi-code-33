from .AbstractEstimator import AbstractEstimator
import numpy as np


class PafkaKondorOracleEstimator(AbstractEstimator):
    def __init__(self):
        super().__init__()

    def estimate_eigenvalues(self, sample_est_eigenvectors_array, sample_est_oos_matrix, n_outliers=0):

        N, _ = sample_est_oos_matrix.shape

        return np.array(
            [
                sample_est_eigenvectors_array[:, i] @ sample_est_oos_matrix @ sample_est_eigenvectors_array[:, i]
                for i in range(N - n_outliers)
            ]
        )
