from typing import Any, Callable, Iterable

from bgez.core import Pyon

__all__ = [
    'Disposable',
    'DisposableList',
]

class Disposable:

    @classmethod
    def Is(cls, object: Any) -> bool:
        return hasattr(object, 'dispose')

    @classmethod
    def Create(cls, callback: Callable) -> 'Disposable':
        return Pyon(dispose = callback)

    def dispose(self) -> None:
        '''Execute actions to dispose of this object'''

class DisposableList(Disposable, list):
    '''List of disposables'''

    def yield_items(self) -> Iterable:
        '''Override this function to change the order of the iterations'''
        while self:
            yield self.pop()

    def dispose(self) -> None:
        for item in self.yield_items():
            item.dispose()
