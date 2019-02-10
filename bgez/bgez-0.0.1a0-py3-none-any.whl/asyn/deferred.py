from typing import TypeVar, Generic, Any, Callable

from promise import Promise

__all__ = [
    'Promise',
    'Deferred',
]

T = TypeVar('T')
class Deferred(Generic[T]):

    def __extract(self, resolve, reject):
        self.__resolve: Callable[[Any], None] = resolve
        self.__reject: Callable[[Exception], None] = reject

    def __init__(self):
        self.promise = Promise[T](self.__extract)

    def resolve(self, value: Any) -> None:
        self.__resolve(value)

    def reject(self, reason: Exception) -> None:
        self.__reject(reason)
