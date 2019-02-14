import abc
from typing import Generic, TypeVar, Tuple
from traceback import FrameSummary

from amino import ADT, Either, Right, Left, Dat, Nil
from amino.util.trace import cframe
from amino.state import State
from amino.compute.exception import ComputeException

A = TypeVar('A')
B = TypeVar('B')


class CResult(Generic[A], ADT['CResult[A]']):

    @abc.abstractproperty
    def to_either(self) -> Either[Exception, A]:
        ...


class CSuccess(Generic[A], CResult[A]):

    def __init__(self, value: A) -> None:
        self.value = value

    @property
    def to_either(self) -> Either[Exception, A]:
        return Right(self.value)


class CError(Generic[A], CResult[A]):

    def __init__(self, error: str) -> None:
        self.error = error

    @property
    def to_either(self) -> Either[Exception, A]:
        return Left(Exception(self.error))


class CFatal(Generic[A], CResult[A]):

    def __init__(self, exception: Exception) -> None:
        self.exception = exception

    @property
    def to_either(self) -> Either[Exception, A]:
        return Left(self.exception)


class Thunk(Generic[A, B], Dat['Thunk[A, B]']):

    @staticmethod
    def cons(thunk: State[A, B], frame: FrameSummary=None) -> 'Thunk[A, B]':
        return Thunk(thunk, frame or cframe())

    def __init__(self, thunk: State[A, B], frame: FrameSummary) -> None:
        self.thunk = thunk
        self.frame = frame


def eval_thunk(resource: A, thunk: Thunk[A, B]) -> Tuple[A, B]:
    try:
        return thunk.thunk.run(resource).value
    except ComputeException as e:
        raise e
    except Exception as e:
        raise ComputeException('', Nil, e, thunk.frame)


__all__ = ('CResult', 'NSuccess', 'NError', 'NFatal', 'Thunk', 'eval_thunk')
