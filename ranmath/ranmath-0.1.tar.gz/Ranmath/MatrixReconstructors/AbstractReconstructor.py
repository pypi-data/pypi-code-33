
from abc import ABC, abstractmethod


class AbstractReconstructor(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def reconstruct(self, *params):
        pass
