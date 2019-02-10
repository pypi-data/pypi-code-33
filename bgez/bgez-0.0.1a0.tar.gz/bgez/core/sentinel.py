from weakref import finalize
from typing import Callable

from bgez.core import CallbackList

__all__ = [
    'Sentinel',
]

class Sentinel:
    '''
    Object that monitors its own garbage collection.
    '''

    def __init__(self, callback: Callable = None):
        self._callbacks = callbacks = CallbackList()
        if callback: self._callbacks.append(callback)
        self._finalizer = finalize(self, callbacks.__call__)

    def append(self, callback: Callable):
        return self._callbacks.append(callback)

    def remove(self, callback: Callable):
        return self._callbacks.try_remove(callback)
