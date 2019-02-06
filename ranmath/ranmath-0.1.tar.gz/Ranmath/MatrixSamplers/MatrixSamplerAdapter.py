
from .RollingWindowSampler import RollingWindowSampler
from .GlobalSampler import GlobalSampler

from weakref import ReferenceType


class MatrixSamplerAdapter:

    def __init__(self, matrix_reference: ReferenceType):
        self.matrix_reference = matrix_reference

    def rw_autocorrelation_eigenvalues(self, sample_size: int, out_of_sample_size: int, verbose=False):

        sampler = RollingWindowSampler(sample_size, out_of_sample_size)
        return sampler.autocorrelation_eigenvalues(self.matrix_reference(), verbose=verbose)

    def rw_autocorrelation_eigenvectors(self, sample_size: int, out_of_sample_size: int, verbose=False):

        sampler = RollingWindowSampler(sample_size, out_of_sample_size)
        return sampler.autocorrelation_eigenvectors(self.matrix_reference(), verbose=verbose)

    def rw_sample_estimator_cubes(self, sample_size: int, out_of_sample_size: int, verbose=False):

        sampler = RollingWindowSampler(sample_size, out_of_sample_size)
        return sampler.sample_estimator_cubes(self.matrix_reference(), verbose=verbose)

    def rw_data_cubes(self, sample_size: int, out_of_sample_size: int, verbose=False):

        sampler = RollingWindowSampler(sample_size, out_of_sample_size)
        return sampler.data_cubes(self.matrix_reference(), verbose=verbose)

    def global_eigenvalues(self, verbose=False):

        sampler = GlobalSampler()
        return sampler.autocorrelation_eigenvalues(self.matrix_reference(), verbose=verbose)

    def global_eigenvectors(self, verbose=False):

        sampler = GlobalSampler()
        return sampler.autocorrelation_eigenvectors(self.matrix_reference(), verbose=verbose)

    def global_sample_estimator_cube(self, verbose=False):

        sampler = GlobalSampler()
        return sampler.sample_estimator_cube(self.matrix_reference(), verbose=verbose)