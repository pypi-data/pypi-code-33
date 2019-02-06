
from abc import ABC, abstractmethod


class AbstractSampler(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def autocorrelation_eigenvalues(self, matrix, verbose=False):
        pass

    @abstractmethod
    def autocorrelation_eigenvectors(self, matrix, verbose=False):
        pass
