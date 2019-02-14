from typing import Callable, TypeVar, Any, Generic

from amino.test.spec_spec import Spec
from amino.typeclass.typeclass import instance
from amino.typeclass.functor import Functor, fmap

A = TypeVar('A')
B = TypeVar('B')
F = TypeVar('F')

_A = TypeVar('_A')

class TMaybe(Generic[_A]):
    pass


class TJust(TMaybe[_A]):

    def __init__(self, value: _A) -> None:
        self.value = value


class _Nothing(TMaybe[_A]):
    pass


TNothing: TMaybe[Any] = _Nothing()


def fmap_maybe(f: Callable[[A], B], fa: TMaybe[A]) -> TMaybe[B]:
    return TJust(f(fa.value)) if isinstance(fa, TJust) else TNothing


maybe_instance = instance(Functor, TMaybe, fmap=fmap_maybe)


class _TypeclassSpec(Spec):

    def fmap(self) -> None:
        print(fmap(lambda a: a + 1)(TJust(1)))


__all__ = ('_TypeclassSpec',)
