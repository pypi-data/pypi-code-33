from typing import TypeVar, Callable

from amino.tc.monad import Monad
from amino.tc.base import ImplicitInstances
from amino.lazy import lazy
from amino import Map
from amino.compute.compute import Compute, ComputePure, flat_map_compute

A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')


class ComputeInstances(ImplicitInstances):

    @lazy
    def _instances(self) -> Map:
        return Map({Monad: ComputeMonad()})


class ComputeMonad(Monad[Compute]):

    def pure(self, a: A) -> Compute[S, A]:
        return ComputePure(a)

    def flat_map(self, fa: Compute[S, A], f: Callable[[A], Compute[S, B]]) -> Compute[S, B]:
        return flat_map_compute(f)(fa)


__all__ = ('ComputeInstances', 'ComputeMonad')
