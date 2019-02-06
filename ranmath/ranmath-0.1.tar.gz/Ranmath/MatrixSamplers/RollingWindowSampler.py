
import numpy as np
import scipy.linalg as la
from collections import namedtuple

from .AbstractSampler import AbstractSampler


class RollingWindowSampler(AbstractSampler):

    def __init__(self, sample_size: int, out_of_sample_size: int):
        super().__init__()
        self.__sample_size = sample_size
        self.__out_of_sample_size = out_of_sample_size

    def autocorrelation_eigenvalues(self, matrix, verbose=False):

        if verbose:
            print("Fetching eigenvalues")

        n_iter, N, T = matrix.array.shape

        sample_cube, out_of_sample_cube = self.sample_estimator_cubes(matrix, verbose=verbose)

        sample_eigenvalues, out_of_sample_eigenvalues = [], []

        for iteration in range(n_iter):

            sample_eigenvalues.append([])
            out_of_sample_eigenvalues.append([])

            for matrix in sample_cube[iteration]:
                sample_eigenvalues[iteration].append(la.eigvals(matrix))

            for matrix in out_of_sample_cube[iteration]:
                out_of_sample_eigenvalues[iteration].append(la.eigvals(matrix))

        eigenvalues = namedtuple("Eigenvalues", ["sample_eigenvalues", "out_of_sample_eigenvalues"]) \
            (np.array(sample_eigenvalues), np.array(out_of_sample_eigenvalues))

        return eigenvalues

    def autocorrelation_eigenvectors(self, matrix, verbose=False):

        if verbose:
            print("Fetching eigenvectors")

        n_iter, N, T = matrix.array.shape

        sample_cube, out_of_sample_cube = self.sample_estimator_cubes(matrix, verbose=verbose)

        sample_eigenvectors, out_of_sample_eigenvectors = [], []

        for iteration in range(n_iter):

            sample_eigenvectors.append([])
            out_of_sample_eigenvectors.append([])

            for matrix in sample_cube[iteration]:
                sample_eigenvectors[iteration].append(la.eig(matrix)[1])

            for matrix in out_of_sample_cube[iteration]:
                out_of_sample_eigenvectors[iteration].append(la.eig(matrix)[1])

        eigenvectors = namedtuple("Eigenvectors", ["sample_eigenvectors", "out_of_sample_eigenvectors"]) \
            (np.array(sample_eigenvectors), np.array(out_of_sample_eigenvectors))

        return eigenvectors

    def sample_estimator_cubes(self, matrix, verbose=False):

        if verbose:
            print("Fetching covariance cubes")

        n_iter, N, T = matrix.array.shape

        window_size = self.__sample_size + self.__out_of_sample_size

        sample_cube, out_of_sample_cube = [], []

        for iteration in range(n_iter):

            sample_cube.append([])
            out_of_sample_cube.append([])

            for k in range(len(matrix.array[0]) - window_size + 1):

                sample_border = k + self.__sample_size

                sample = matrix.array[iteration, :, k: sample_border]
                out_of_sample = matrix.array[iteration, :, sample_border: sample_border + self.__out_of_sample_size]

                T = matrix.array.shape[1]

                sample_cube[iteration].append(sample @ sample.T / self.__sample_size)
                out_of_sample_cube[iteration].append(out_of_sample @ out_of_sample.T / self.__out_of_sample_size)

        covariance_cubes = namedtuple("CovarianceCubes", ['sample_cube', 'out_of_sample_cube']) \
            (np.array(sample_cube), np.array(out_of_sample_cube))

        return covariance_cubes

    def data_cubes(self, matrix, verbose=False):

        if verbose:
            print("Fetching data cubes")

        n_iter, N, T = matrix.array.shape

        window_size = self.__sample_size + self.__out_of_sample_size

        sample_cube, out_of_sample_cube = [], []

        for iteration in range(n_iter):

            sample_cube.append([])
            out_of_sample_cube.append([])

            for k in range(len(matrix.array[0]) - window_size + 1):

                sample_border = k + self.__sample_size

                sample = matrix.array[iteration, :, k: sample_border]
                out_of_sample = matrix.array[iteration, :, sample_border: sample_border + self.__out_of_sample_size]

                sample_cube[iteration].append(sample)
                out_of_sample_cube[iteration].append(out_of_sample)

        covariance_cubes = namedtuple("DataCubes", ['sample_cube', 'out_of_sample_cube']) \
            (np.array(sample_cube), np.array(out_of_sample_cube))

        return covariance_cubes

