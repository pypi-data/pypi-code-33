from typing import TypeVar, Callable, Generic, Tuple, cast

from amino.tc.base import F, ImplicitsMeta, Implicits
from amino import Either, List, options, Do, Boolean
from amino.state import State
from amino.do import do
from amino.dat import ADT, ADTMeta
from amino.case import Case, CaseRec, Term, RecStep
from amino.logging import module_log
from amino.compute.data import CResult, CFatal, Thunk, CSuccess, CError, eval_thunk
from amino.compute.exception import ComputeException

log = module_log()
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
S = TypeVar('S')
debug = options.io_debug.exists


class ComputeMeta(ImplicitsMeta, ADTMeta):
    pass


class Compute(
        Generic[S, A],
        Implicits,
        ADT['Compute[S, A]'],
        implicits=True,
        imp_mod='amino.compute.tc',
        metaclass=ComputeMeta,
):

    def eval(self) -> State[S, CResult[A]]:
        return eval_compute(self)

    def run(self, vim: S) -> Tuple[S, CResult[A]]:
        try:
            return self.eval().run(vim).value
        except ComputeException as e:
            return vim, CFatal(e)

    def run_s(self, vim: S) -> S:
        return self.run(vim)[0]

    def run_a(self, vim: S) -> CResult[A]:
        return self.run(vim)[1]

    result = run_a

    def either(self, vim: S) -> Either[ComputeException, A]:
        return self.result(vim).to_either

    def unsafe_run(self, vim: S) -> Tuple[S, A]:
        result_vim, result = self.run(vim)
        return result_vim, result.to_either.get_or_raise()

    def unsafe(self, vim: S) -> A:
        return self.either(vim).get_or_raise()


class ComputePure(Generic[S, A], Compute[S, A]):

    def __init__(self, value: A) -> None:
        self.value = value


class ComputeSuspend(Generic[S, A], Compute[S, A]):

    @staticmethod
    def cons(thunk: State[S, Compute[S, A]]) -> 'ComputeSuspend[S, A]':
        return ComputeSuspend(Thunk.cons(thunk))

    def __init__(self, thunk: Thunk[S, Compute[S, A]]) -> None:
        self.thunk = thunk


class ComputeBind(Generic[S, A, B], Compute[S, B]):

    def __init__(
            self,
            thunk: Thunk[S, Compute[S, A]],
            kleisli: Callable[[A], Compute[S, B]],
    ) -> None:
        self.thunk = thunk
        self.kleisli = kleisli


class ComputeError(Generic[S, A], Compute[S, A]):

    def __init__(self, error: str) -> None:
        self.error = error


class ComputeFatal(Generic[S, A], Compute[S, A]):

    def __init__(self, exception: Exception) -> None:
        self.exception = exception


class ComputeRecover(Generic[S, A], Compute[S, A]):

    def __init__(
            self,
            io: Compute[S, A],
            recover: Callable[[CResult[A]], Compute[S, A]],
            recoverable: Callable[[CResult[A]], Boolean],
    ) -> None:
        self.io = io
        self.recover = recover
        self.recoverable = recoverable


class lift_n_result(Case[CResult[A], Compute[S, A]], alg=CResult):

    def n_success(self, result: CSuccess[A]) -> Compute[S, A]:
        return ComputePure(result.value)

    def n_error(self, result: CError[A]) -> Compute[S, A]:
        return ComputeError(result.error)

    def n_fatal(self, result: CFatal[A]) -> Compute[S, A]:
        return ComputeFatal(result.exception)


@do(State[S, Compute[S, Either[List[str], A]]])
def execute_compute_recover(io: ComputeRecover[S, A]) -> Do:
    def execute_wrapped(vim: S) -> Tuple[S, Either[List[str], A]]:
        updated_vim, result = io.io.run(vim)
        return updated_vim, (
            io.recover(result)
            if io.recoverable(result) else
            lift_n_result.match(result)
        )
    updated_vim, result = yield State.inspect(execute_wrapped)
    yield State.reset(updated_vim, result)


class flat_map_compute(Generic[S, A, B], Case[Callable[[A], Compute[S, B]], Compute[S, B]], alg=Compute):

    def __init__(self, f: Callable[[A], Compute[S, B]]) -> None:
        self.f = f

    def compute_pure(self, io: ComputePure[S, A]) -> Compute[S, B]:
        thunk = State.delay(self.f, io.value)
        return ComputeSuspend.cons(thunk)

    def compute_suspend(self, io: ComputeSuspend[S, A]) -> Compute[S, B]:
        return ComputeBind(io.thunk, self.f)

    def compute_bind(self, io: ComputeBind[S, C, A]) -> Compute[S, B]:
        return ComputeSuspend.cons(State.pure(ComputeBind(io.thunk, lambda a: io.kleisli(a).flat_map(self.f))))

    def compute_error(self, io: ComputeError[S, A]) -> Compute[S, B]:
        return cast(Compute[S, B], io)

    def compute_fatal(self, io: ComputeFatal[S, A]) -> Compute[S, B]:
        return cast(Compute[S, B], io)

    def compute_recover(self, io: ComputeRecover[S, A]) -> Compute[S, B]:
        return ComputeBind(Thunk.cons(execute_compute_recover(io)), self.f)


EvalRes = RecStep[Compute[S, A], Tuple[S, CResult[A]]]


class eval_step(Generic[S, A], CaseRec[Compute[S, A], CResult[A]], alg=Compute):

    def __init__(self, vim: S) -> None:
        self.vim = vim

    def compute_pure(self, io: ComputePure[S, A]) -> EvalRes:
        return Term((self.vim, CSuccess(io.value)))

    def compute_suspend(self, io: ComputeSuspend[S, A]) -> EvalRes:
        vim, next = eval_thunk(self.vim, io.thunk)
        return eval_step(vim)(next)

    def compute_bind(self, io: ComputeBind[S, B, A]) -> EvalRes:
        vim, next = eval_thunk(self.vim, io.thunk)
        return eval_step(vim)(next.flat_map(io.kleisli))

    def compute_error(self, io: ComputeError[S, A]) -> EvalRes:
        return Term((self.vim, CError(io.error)))

    def compute_fatal(self, io: ComputeFatal[S, A]) -> EvalRes:
        return Term((self.vim, CFatal(io.exception)))

    def compute_recover(self, io: ComputeRecover[S, A]) -> Compute[S, B]:
        '''calls `map` to shift the recover execution to flat_map_compute
        '''
        return eval_step(self.vim)(io.map(lambda a: a))


@do(State[S, A])
def eval_compute(io: Compute[S, A]) -> Do:
    vim = yield State.get()
    updated_vim, result = eval_step(vim)(io).eval()
    yield State.set(updated_vim)
    return result


__all__ = ('Compute',)
