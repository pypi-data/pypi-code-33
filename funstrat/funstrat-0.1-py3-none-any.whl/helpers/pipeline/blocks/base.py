# import abc
from abc import ABCMeta, ABC, abstractmethod


class BaseBlock(ABC):
    def __init__(self):
        pass
    

    @abstractmethod
    def process(self):
        raise NotImplementedError("Processing Block not implemented")