"""
Seedflow.

Side Effects As Data -> SEAD -> Seed.
Flow, because the library supports muliple concurrent flows of logic/side-effects.
"""


# [ Imports:Future ]
from __future__ import annotations

# [ Imports:Python ]
import abc
import collections
import enum
import functools
import inspect
import random
import signal
import sys
import time
import types
import typing
from concurrent import futures

# [ Imports:Third Party ]
import din
import pipe
import rototiller


# [ Internal ]
_GenericTypeVar = typing.TypeVar('_GenericTypeVar')
_ReturnTypeVar = typing.TypeVar('_ReturnTypeVar')


# [ API ]
class ReturnType(din.EqualityMixin, din.ReprMixin, abc.ABC):
    """A return type abc."""

    pass


class Value(ReturnType):
    """A value returned by a spawned flow."""

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class Error(ReturnType):
    """An error raised by a spawned flow."""

    def __init__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_value: typing.Optional[BaseException],
        exc_traceback: typing.Optional[types.TracebackType],
    ):
        super().__init__()
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback
        self._error_dict = exc_value.__dict__
        self._repr_attributes = ('value',)
        self._equality_attributes = ('_error_dict',)


class Cancelled(din.EqualityMixin, din.ReprMixin):
    """Indicates that a subflow has beeen cancelled."""

    pass


class Spawned(din.EqualityMixin, din.ReprMixin):
    """Indicates that a subflow has been spawned, but has not yet completed."""

    pass


# [ Internal ]
_ExcInfoType = typing.Tuple[
    typing.Optional[typing.Type[BaseException]],
    typing.Optional[BaseException],
    typing.Optional[types.TracebackType],
]
_TaskCoroType = rototiller.Coro['Task', typing.Any, _ReturnTypeVar]
_TaskFuncType = rototiller.WrappableFuncType['Task', typing.Any, _ReturnTypeVar]
_SyncFuncType = typing.Callable[..., _ReturnTypeVar]


def _strip_traceback(
    traceback: typing.Optional[types.TracebackType],
) -> typing.Optional[types.TracebackType]:
    while traceback and traceback.tb_frame.f_globals['__name__'] in (__name__, 'rototiller', 'concurrent.futures._base', 'concurrent.futures.thread'):
        traceback = traceback.tb_next
    if traceback:
        traceback.tb_next = _strip_traceback(traceback.tb_next)
    return traceback


class Sentinels(enum.Enum):
    """Sentinels with more explicit and constrained meaning than None."""

    UNSET = enum.auto()


_THREAD_EXECUTOR = futures.ThreadPoolExecutor(thread_name_prefix='seedflow')


# [ API ]
# Exposing internals because mypy doesn't allow forward references of generic types.
TaskFuncType = _TaskFuncType[_ReturnTypeVar]
SyncFuncType = _SyncFuncType[_ReturnTypeVar]


# pylint is wrong about typing.Generic
class Task(din.ReprMixin, din.FrozenMixin, din.EqualityMixin):  # pylint: disable=unsubscriptable-object
    """The base run that the seedflow runner executes."""

    def __init__(  # noqa
        self,
        func: typing.Callable,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        with self._thawed():
            super().__init__()
            self.func = func
            self.args = args
            self.kwargs = kwargs

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"[seedflow.Task]",
            f"  func: {self.func.__module__}.{self.func.__qualname__}",
            f"  args:",
            *("\n".join(f"    {l}" for l in f"{a}".splitlines()) for a in self.args),
            f"  kwargs:",
            *("\n".join(f"    {l}" for l in f"{k}: {v}".splitlines()) for k, v in self.kwargs.items()),
        ]
        return "\n".join(lines)


# pylint is wrong about typing.Generic
class TailCall(din.EqualityMixin, Exception, typing.Generic[_ReturnTypeVar]):  # pylint: disable=unsubscriptable-object
    """Tail Call Optimization helper class."""

    def __init__(  # noqa
        self,
        func: typing.Callable,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __str__(self) -> str:  # pragma: no cover
        lines = [
            f"[seedflow.TailCall]",
            f"  func: {self.func.__module__}.{self.func.__qualname__}",
            f"  args:",
            *("\n".join(f"    {l}" for l in f"{a}".splitlines()) for a in self.args),
            f"  kwargs:",
            *("\n".join(f"    {l}" for l in f"{k}: {v}".splitlines()) for k, v in self.kwargs.items()),
        ]
        return "\n".join(lines)

    __repr__ = __str__


def as_sync(
    func: TaskFuncType[_ReturnTypeVar],
) -> SyncFuncType[_ReturnTypeVar]:
    """
    Decorate an awaitable such that it is run with seedflow when called.

    This makes a seedflow-awaitable function callable from a synchronous context.
    """
    @functools.wraps(func)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> _ReturnTypeVar:
        return run_sync(func, *args, **kwargs)
    return _wrapper


def _init_flow(new_flow, *, flows):
    task = new_flow.task
    # if the func is a normal func, just run it
    if not callable(task.func):
        raise RuntimeError(f"Provided task function is not callable: {task.func}")
    if not inspect.iscoroutinefunction(task.func):
        future = _THREAD_EXECUTOR.submit(task.func, *task.args, **task.kwargs)
        new_flow.future = future
    else:
        # otherwise wrap it up with rototiller
        new_flow.coro = rototiller.Coro(task.func)
        # it's a coroutine.  We want to call it with args/kwargs,
        # and rather than a normal function returning a value, one
        # way to look at it is this thing is going to ask us for
        # something in return.  We'll init, and it will request.
        new_flow.request = new_flow.coro.init(*task.args, **task.kwargs)
    flows.append(new_flow)
    return flows


@pipe.Pipe
def _isinstance_p(thing, type_):
    return isinstance(thing, type_)


class SpawnRequest(din.EqualityMixin, din.ReprMixin):
    """A request from a flow to spawn a new subflow."""

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs


@types.coroutine
def spawn(func, *args, **kwargs):
    """Spawn a subflow, and return that flow's id."""
    return (yield SpawnRequest(func, *args, **kwargs))


class CancelRequest(din.EqualityMixin, din.ReprMixin):
    """A request from a flow to cancel all the unfinished subflows."""

    pass


@types.coroutine
def cancel_remaining():
    """
    Cancel all remaining subflows which have not completed yet.

    Sets the results for these flows to an instance of `Cancelled`.
    """
    return (yield CancelRequest())


class ResultsRequest:
    """A Request from a flow for the next available results from its subflows."""

    pass


@types.coroutine
def get_results():
    """
    Get results for this flow's spawned subflows.

    Results will be returned in a dictionary of available flow ID's as keys
    and their results as values.  The results will be `Value` or `Error` objects
    """
    return (yield ResultsRequest())


def _create_unique_flow_id(flows):
    # this is not a cryptographic use of random numbers - it's here for internal uniqueness,
    # not to prevent prediction or spoofing or anything.
    this_id = random.randint(0, 2**64)  # nosec
    limit = 100
    tries = 1
    while this_id in flows and tries < limit:  # pragma: no coverage
        # this is a safety net - we should cover it if it gets pulled out
        # this is not a cryptographic use of random numbers - it's here for internal uniqueness,
        # not to prevent prediction or spoofing or anything.
        this_id = random.randint(0, 2**64)  # nosec
        tries += 1
    if this_id in flows:  # pragma: no coverage
        # this is a safety net - we should cover it if it gets pulled out
        raise RuntimeError(
            f'After {tries} attempts, we could not generate a unique ID for a new flow.'
            f'  There are {len(flows)} flows currently recorded.',
        )
    return this_id


# For now, not sure how to decrease the attributes.
# Ironically, this was not a problem when this was a dictionary,
# but now that I made it better (a real data type), pylint
# complains.
class _Flow(din.EqualityMixin, din.ReprMixin):  # pylint: disable=too-many-instance-attributes
    def __init__(self, task, *, id_, parent_id=None):
        super().__init__()
        self.parent_id = parent_id
        self.id_ = id_
        self.task = task

        # XXX don't like the combo coro/future here.  Maybe different flow subtypes?
        self.coro = None
        self.future = None

        # XXX should request/requesting-flow pairs be stored separately
        #     rather than as a property on the requesting flow?
        self.request = None

        # XXX shouldn't need both subflow results (results from subflows) and our results stored here
        #     (our results should just get set on the parent flow, or returned/raised, right?)
        # XXX also same concern as above re: pairs vs properties.  The child results/our-results
        #     aren't even really part of the flow itself.
        self.subflow_results = {}
        self.result = Sentinels.UNSET


@pipe.Pipe
def _is_uninitialized(flow):
    return flow.request is None and flow.future is None


@pipe.Pipe
def _has_future(flow):
    return flow.request is None and flow.future


def _check_flow_future(thread_flow, *, flows):
    if thread_flow.future.done():
        try:
            thread_flow.request = rototiller.Returned(thread_flow.future.result())
        # necessarily broad exception handling - we want to wrap all standard exceptions
        except Exception:  # pylint: disable=broad-except
            thread_flow.request = rototiller.Raised(*sys.exc_info())
    flows.append(thread_flow)
    return flows


@pipe.Pipe
def _requested_to_return(flow):
    return flow.request | _isinstance_p(rototiller.Returned)


@pipe.Pipe
def _requested_to_raise(flow):
    return flow.request | _isinstance_p(rototiller.Raised)


def _verify_no_orphan_subflows(flows, *, parent):
    outstanding_child_flows = [f for f in flows if f.parent_id == parent.id_]
    if outstanding_child_flows:
        children_str = '\n'.join((str(ocf) for ocf in outstanding_child_flows))
        error = RuntimeError(
            f"Flow {parent} completed before handling outstanding child flows:\n{children_str}",
        )
        if parent | _requested_to_raise:
            raise error from parent.request.exc_value.with_traceback(parent.request.exc_traceback)
        raise error


def _verify_no_orphan_results(flow):
    if flow.subflow_results:  # pragma: no coverage
        # theoretically this could happen, but I'm not sure how to force it to right now -
        # the only way to trigger this without triggering the above would be to allow subflows
        # to complete before asking for results and before returning, which would require a
        # different kind of request to be created.
        error = RuntimeError(
            f"Flow {flow} returned before handling results from completed"
            f" child flows:"
            '\n'.join((str(sr) for sr in flow.subflow_results)),
        )
        if flow | _requested_to_raise:
            raise error from flow.request.exc_value.with_traceback(flow.request.exc_traceback)
        raise error


@pipe.Pipe
def _has_parent(flow):
    return flow.parent_id is not None


def _return_to_parent(subflow, *, flows):
    # if parent requested results, send to parent, record parent's request
    possible_parents = [f for f in flows if f.id_ == subflow.parent_id]
    if not possible_parents:  # pragma: no coverage
        # this is for programming mistake debugging for the library
        raise RuntimeError(f"Flow's parent can't be found: {subflow}")
    parent, *others = possible_parents
    if others:  # pragma: no coverage
        # another library programming mistake catch
        other_strings = '\n'.join((str(o) for o in others))
        raise RuntimeError(
            f"Multiple flows with the same id ({subflow.parent_id}):\n"
            f"{parent}\n{other_strings}",
        )
    if (
        parent.request | _isinstance_p(rototiller.Yielded)
            and parent.request.value | _isinstance_p(ResultsRequest)
    ):
        parent.request = parent.coro.send({subflow.id_: Value(subflow.request.value)})
    # if parent did not request results, record result on parent
    else:
        parent.subflow_results[subflow.id_] = Value(subflow.request.value)


def _raise_to_parent(subflow, *, flows):
    # if parent requested results, send to parent, record parent's request
    possible_parents = [f for f in flows if f.id_ == subflow.parent_id]
    if not possible_parents:  # pragma: no cover
        # not sure how to create the scenario for this
        raise RuntimeError(
            f"Flow's parent can't be found: {subflow}",
        ) from subflow.request.exc_value.with_traceback(subflow.request.exc_traceback)
    parent, *others = possible_parents
    if others:  # pragma: no cover
        # not sure how to create the scenario for this
        other_strings = '\n'.join((str(o) for o in others))
        raise RuntimeError(
            f"Multiple flows with the same id ({subflow.parent_id}):\n"
            f"{parent}\n{other_strings}",
        ) from subflow.request.exc_value.with_traceback(subflow.request.exc_traceback)
    if (
        parent.request | _isinstance_p(rototiller.Yielded)
            and parent.request.value | _isinstance_p(ResultsRequest)
    ):
        parent.request = parent.coro.send({subflow.id_: Error(*subflow.request.value)})
    # if parent did not request results, record result on parent
    else:
        parent.subflow_results[subflow.id_] = Error(*subflow.request.value)


def _verify_no_remaining_flows(main_flow, *, flows):
    if flows:  # pragma: no coverage
        # this is another spot that is here to handle terrible behavior - library errors,
        # or something else utterly unexpected.  at the time of writing, I don't see a way
        # to trigger this non-artificially for testing.
        orphans = '\n'.join((str(f) for f in flows))
        error = RuntimeError(
            f"When returning main flow {main_flow}, orphan flows"
            f" remain:\n{orphans}",
        )
        if main_flow | _requested_to_raise:
            raise error from main_flow.request.exc_value.with_traceback(main_flow.request.exc_traceback)
        raise error


@pipe.Pipe
def _requested_tco(flow):
    return (
        flow.request | _isinstance_p(rototiller.Raised)
        and flow.request.exc_value | _isinstance_p(TailCall)
    )


def _optimize_tail_call(tco_flow, *, flows):
    tco_flow.task = tco_flow.request.exc_value
    tco_flow.coro = None
    tco_flow.request = None
    tco_flow.future = None
    flows.append(tco_flow)
    return flows


@pipe.Pipe
def _requested_to_spawn_subflow(flow):
    return (
        flow.request | _isinstance_p(rototiller.Yielded)
        and flow.request.value | _isinstance_p(SpawnRequest)
    )


def _spawn_subflow(parent, *, flows):
    # spawn the subflow
    subflow = _Flow(
        Task(parent.request.value.func, *parent.request.value.args, **parent.request.value.kwargs),
        id_=_create_unique_flow_id(flows),
        parent_id=parent.id_,
    )
    # send the id back
    # record the new request
    parent.request = parent.coro.send(subflow.id_)
    flows += (subflow, parent)
    return flows


@pipe.Pipe
def _requested_results(flow):
    return (
        flow.request | _isinstance_p(rototiller.Yielded)
        and flow.request.value | _isinstance_p(ResultsRequest)
    )


def _send_results_back(parent, *, flows):
    # if requests stored on flow record
    if parent.subflow_results:
        # remove them
        results = parent.subflow_results
        parent.subflow_results = {}
        # send them
        # record the new request
        parent.request = parent.coro.send(results)
    # else if no flows children for flow, error
    elif not [f for f in flows if f.parent_id == parent.id_]:
        raise RuntimeError(f"cannot wait for results - there are no child flows for {parent}")
    flows.append(parent)
    return flows


@pipe.Pipe
def _requested_subflow_cancellation(flow):
    return (
        flow.request | _isinstance_p(rototiller.Yielded)
        and flow.request.value | _isinstance_p(CancelRequest)
    )


def _cancel_subflows(parent, *, flows):
    # subflows to cancel
    active_subflows = [f for f in flows if f.parent_id == parent.id_]
    # cancel subflows all the way down
    to_cancel = collections.deque(active_subflows)
    while to_cancel:
        this_subflow = to_cancel.popleft()
        if this_subflow.coro:
            this_subflow.coro.close()
        flows.remove(this_subflow)
        sub_subflows = [f for f in flows if f.parent_id == this_subflow.id_]
        to_cancel += sub_subflows
    # set the results
    parent.subflow_results.update({s.id_: Cancelled() for s in active_subflows})
    # if requests stored on flow record
    results = parent.subflow_results
    parent.subflow_results = {}
    parent.request = parent.coro.send(results)
    flows.append(parent)
    return flows


@pipe.Pipe
def _completed(flow):
    return flow | _requested_to_return or flow | _requested_to_raise


def _handle_completed_flow(completed_flow, *, flows):
    _verify_no_orphan_subflows(flows, parent=completed_flow)
    _verify_no_orphan_results(completed_flow)
    if completed_flow | _has_parent:
        if completed_flow | _requested_to_return:
            _return_to_parent(completed_flow, flows=flows)
        elif completed_flow | _requested_to_raise:
            _raise_to_parent(completed_flow, flows=flows)
        else:  # pragma: no coverage
            # not sure how to trigger this in a test
            raise RuntimeError(f'Unknown request type: {completed_flow.request}')
    else:
        _verify_no_remaining_flows(completed_flow, flows=flows)
    return flows


def run_sync(func, *args, **kwargs):
    """
    Run the given func synchronously.

    The function may be sync or async.  It will be run to completion, and
    the output returned, or exception raised.
    """
    flows = collections.deque()
    # treat initial run as a spawn
    this_flow = _Flow(
        Task(func, *args, **kwargs),
        id_=_create_unique_flow_id(flows),
    )
    flows.append(this_flow)
    while flows:
        this_flow = flows.popleft()
        for meets_condition, action in {
            _is_uninitialized               : _init_flow,
            _has_future                     : _check_flow_future,
            _requested_tco                  : _optimize_tail_call,
            _requested_to_spawn_subflow     : _spawn_subflow,
            _requested_results              : _send_results_back,
            _requested_subflow_cancellation : _cancel_subflows,
            _completed                      : _handle_completed_flow,
        }.items():
            if this_flow | meets_condition:
                flows = action(this_flow, flows=flows)
                break
        else:
            raise RuntimeError(f'Flow in unknown condition: {this_flow}')
    # no flows left.  return/raise the final result to the caller.
    if this_flow | _requested_to_return:
        return this_flow.request.value
    raise this_flow.request.exc_value.with_traceback(_strip_traceback(this_flow.request.exc_traceback))


async def till_all(*tasks: Task) -> typing.Tuple[ReturnType, ...]:
    """Run the tasks till all complete."""
    def all_done(results):
        return all(not r | _isinstance_p(Spawned) for r in results.values())

    return await till(all_done, *tasks)


async def till_any(*tasks: Task) -> typing.Tuple[ReturnType, ...]:
    """Run till any task is complete."""
    def any_done(results):
        return any(not r | _isinstance_p(Spawned) for r in results.values())

    return await till(any_done, *tasks)


async def till(predicate, *tasks):
    """
    Run the tasks concurrently till the predicate returns True.

    The predicate is called with the result dictionary every time a
    task completes.

    If a task has not completed, its result will be a `Spawned` object.
    """
    flow_ids = [await spawn(t.func, *t.args, **t.kwargs) for t in tasks]
    results = {fid: Spawned() for fid in flow_ids}
    while not predicate(results):
        results.update(await get_results())
    results.update(await cancel_remaining())
    return tuple(results[fid] for fid in flow_ids)


async def run(func, *args, **kwargs):
    """Run the task concurrently with other stuff in the top level runner."""
    flow_id = await spawn(func, *args, **kwargs)
    result = (await get_results())[flow_id]
    if result | _isinstance_p(Value):
        return result.value
    if result | _isinstance_p(Error):
        raise result.exc_value.with_traceback(result.exc_traceback)
    # This is not part of the published API - it's to give a nicer error message if there's a library programming error.
    raise RuntimeError(f"Unknown result type: {result}")  # pragma: no coverage


# this is a default, not a keyword-arg.
async def on_timeout(timeout, func=lambda: None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Run the func once on the given timeout."""
    await run(time.sleep, timeout)
    return await run(func, *args, **kwargs)


# this is a default, not a keyword-arg.
async def on_interval(timeout, func=lambda: None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Run the func on the interval."""
    while True:
        await run(time.sleep, timeout)
        await run(func, *args, **kwargs)


# this is a default, not a keyword-arg.
async def on_signal(signum, func=lambda: None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Run the func the first time the given signal is sent."""
    prev_handler = signal.getsignal(signum)
    triggered = False

    def new_handler(_signum, _frame):
        nonlocal triggered
        signal.signal(signum, prev_handler)
        triggered = True
    signal.signal(signum, new_handler)
    while not triggered:
        await run(lambda: None)
    return await run(func, *args, **kwargs)


# this is a default, not a keyword-arg.
async def on_signal_repeating(signum, func=lambda: None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Run the func every time the given signal is sent."""
    prev_handler = signal.getsignal(signum)
    triggered = False

    def new_handler(_signum, _frame):
        nonlocal triggered
        triggered = True
    try:
        signal.signal(signum, new_handler)
        while True:
            while not triggered:
                await run(lambda: None)
            triggered = False
            await run(func, *args, **kwargs)
    finally:
        signal.signal(signum, prev_handler)
