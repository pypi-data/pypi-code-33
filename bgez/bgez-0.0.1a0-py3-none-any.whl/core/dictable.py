import abc

__all__ = [
    'Dictable',
]

class Dictable(abc.ABC):

    @abc.abstractmethod
    def to_dict(self) -> dict:
        '''Returns this keymap as a dictionnary.'''

    @abc.abstractmethod
    def from_dict(self, data: dict) -> None:
        '''Loads keymap data from the given dictionnary.'''
