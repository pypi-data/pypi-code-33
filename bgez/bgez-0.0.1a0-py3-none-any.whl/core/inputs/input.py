from typing import Generic, TypeVar, Optional, Iterable, Type

import abc

__all__ = [
    'InputType',
    'RawInput',
]

T = TypeVar('T')

class InputType(Generic[T], abc.ABC):
    '''
    A value type represents a specific input space.
    e.g.: A joystick returns a float when a button returns an int.

    Defines two classmethods: `union` and `intersection`.
    '''

    @classmethod
    def _filter(cls, values: Iterable[Optional[T]]) -> Iterable[T]:
        '''Removes `None` values from a sequence.'''
        return filter(lambda value: value is not None, values) # type: ignore

    @classmethod
    @abc.abstractmethod
    def _normalize(cls, values: Iterable[T]) -> Iterable[T]:
        '''Normalize the values of this type'''

    @classmethod
    @abc.abstractmethod
    def _union(cls, values: Iterable[T]) -> T:
        '''Returns the union for the inputs'''

    @classmethod
    @abc.abstractmethod
    def _intersection(cls, values: Iterable[T]) -> T:
        '''Returns the intersection for the inputs'''

    def __init__(self, input: 'RawInput[T]'):
        if not issubclass(input.type, self.__class__):
            raise TypeError(f'{input.type} isn\'t compatible with {self.__class__}')
        self._input = input

    def value(self) -> T:
        return self._input.value()

class RawInput(Generic[T]):
    '''
    An Input represents exactly one input of some sort, from some device.
    '''

    @property
    def type(self) -> Type[InputType[T]]:
        '''The type of this input.'''

    @abc.abstractmethod
    def value(self) -> T:
        '''Returns the value for this specific input.'''
