
from .MultivariateGaussianGenerator import MultivariateGaussianGenerator
from .InverseWishartGenerator import InverseWishartGenerator
from .ExponentialDecayGenerator import ExponentialDecayGenerator

from weakref import ReferenceType


class MatrixGeneratorAdapter:

    def __init__(self, matrix_reference: ReferenceType):
        self.matrix_reference = matrix_reference
        self.__last_C = None
        self.__last_A = None

    @property
    def last_C(self):
        return self.__last_C

    @property
    def last_A(self):
        return self.__last_A

    def multivariate_gaussian(self, C, A, number_of_iteratons: int, verbose=False):

        generator = MultivariateGaussianGenerator(C, A, number_of_iteratons)
        self.matrix_reference().array = generator.generate(verbose)
        self.__last_A = generator.last_A
        self.__last_C = generator.last_C

    def inverse_wishart(self, number_of_assets, number_of_samples, kappa, number_of_iterations: int, normalize_covariance=True, verbose=False):

        generator = InverseWishartGenerator(number_of_assets, number_of_samples, kappa, number_of_iterations, normalize_covariance)
        self.matrix_reference().array = generator.generate(verbose)
        self.__last_A = generator.last_A
        self.__last_C = generator.last_C

    def exponential_decay(self, number_of_assets, number_of_samples, autocorrelation_time, number_of_iterations: int, verbose=False):

        generator = ExponentialDecayGenerator(number_of_assets, number_of_samples, autocorrelation_time, number_of_iterations)
        self.matrix_reference().array = generator.generate(verbose)
        self.__last_A = generator.last_A
        self.__last_C = generator.last_C