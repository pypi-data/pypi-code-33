
from abc import ABC, abstractmethod


class AbstractResolvent(ABC):

    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def compute(*params, verbose=False):
        pass

