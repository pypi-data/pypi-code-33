
from abc import ABC, abstractmethod


class AbstractNormalizer(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def normalize(self, matrix, verbose=False):
        pass
