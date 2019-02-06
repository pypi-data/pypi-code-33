
from abc import ABC, abstractmethod


class AbstractGenerator(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self, verbose=False):
        pass
