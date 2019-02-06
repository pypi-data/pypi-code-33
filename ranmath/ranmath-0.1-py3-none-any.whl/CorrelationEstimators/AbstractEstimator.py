
from abc import ABC, abstractmethod


class AbstractEstimator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def estimate_eigenvalues(*params, verbose=False):
        pass
