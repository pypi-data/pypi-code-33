from typing import Callable, TypeVar

from amino.typeclass.typeclass import Class, Signature, Poly, HK, Nullary, HK1, ClassFunction2, Wildcard

A = TypeVar('A')
B = TypeVar('B')

fmap: ClassFunction2 = ClassFunction2(
    'fmap',
    Signature(
        [
            Poly(HK('F', [Nullary('A')]))
        ],
        Poly(HK('F', [Nullary('B')]))
    ),
    Callable[[A], B],
    HK1[A],
    HK1[B],
)

Functor = Class.cons(
    'Functor',
    params=[Poly(HK('F', [Wildcard()]))],
    functions=[
        fmap,
    ]
)

__all__ = ('Functor',)
