from typing import Callable

import abc

__all__ = [
    'Saveable',
]

class Saveable(abc.ABC):

    @abc.abstractmethod
    def save(self, path: str, *, opener: Callable = open) -> None:
        '''Saves the object at the resource pointed at by `path`.'''

    @abc.abstractmethod
    def load(self, path: str, *, opener: Callable = open) -> None:
        '''Loads the object from the resource pointed at by `path`.'''
