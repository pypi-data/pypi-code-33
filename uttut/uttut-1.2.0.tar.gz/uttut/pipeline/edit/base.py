from collections.abc import Sequence
from abc import abstractmethod, abstractclassmethod


class Group(Sequence):

    def __init__(self):
        self._is_done = False

    @abstractmethod
    def add(self):
        pass

    @abstractclassmethod
    def add_all(cls):
        pass

    @abstractmethod
    def done(self):
        pass

    @abstractmethod
    def _warn_not_done(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass
