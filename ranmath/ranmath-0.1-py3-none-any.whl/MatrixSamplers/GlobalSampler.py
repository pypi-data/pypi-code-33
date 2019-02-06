
import numpy as np
import scipy.linalg as la
from collections import namedtuple

from .AbstractSampler import AbstractSampler


class GlobalSampler(AbstractSampler):

    def __init__(self):
        super().__init__()

    def autocorrelation_eigenvalues(self, matrix, verbose=False):

        if verbose:
            print("Fetching eigenvalues")

        n_iter, N, T = matrix.array.shape

        sample_estimator_cube = self.sample_estimator_cube(matrix, verbose=verbose)

        sample_estimator_eigenvalues = []

        for iteration in range(n_iter):
            sample_estimator_eigenvalues.append(la.eigvals(sample_estimator_cube[iteration]))

        return np.array(sample_estimator_eigenvalues)

    def autocorrelation_eigenvectors(self, matrix, verbose=False):

        if verbose:
            print("Fetching eigenvectors")

        n_iter, N, T = matrix.array.shape

        sample_estimator_cube = self.sample_estimator_cube(matrix, verbose=verbose)

        sample_estimator_eigenvectors = []

        for iteration in range(n_iter):
            sample_estimator_eigenvectors.append(la.eig(sample_estimator_cube[iteration])[1])

        return np.array(sample_estimator_eigenvectors)

    def sample_estimator_cube(self, matrix, verbose=False):

        if verbose:
            print("Fetching sample estimator cube")

        n_iter, N, T = matrix.array.shape

        covariance_cube = []

        for iteration in range(n_iter):
            covariance_cube.append(matrix.array[iteration] @ matrix.array[iteration].T / T)

        return np.array(covariance_cube)
