import functools
import inspect
import logging
import typing

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'SyncSignal', 'AsyncSignal',
    'SyncHook', 'AsyncHook'
]

_log = logging.getLogger(__name__)

T = typing.TypeVar('T')


class BaseSingal(typing.Generic[T]):

    __slots__ = ('name', 'listeners')

    def __init__(self, name: str) -> None:
        self.name: str = name  # pylint: disable=assigning-non-slot
        self.listeners: typing.List[T] = []  # pylint: disable=assigning-non-slot

    def subscribe(self, listener: T) -> None:
        self.listeners.append(listener)

    def unsubscribe(self, listener: T) -> None:
        self.listeners.remove(listener)


class SyncSignal(BaseSingal[typing.Callable[..., None]]):

    __slots__ = ()

    def dispatch(self, *args, **kwargs) -> None:
        for listener in self.listeners:
            listener(*args, **kwargs)

    def dispatch_robust(self, *args, **kwargs) -> None:
        try:
            self.dispatch(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            _log.exception('Exception when processing signal %s: %s', self.name, exc)

    @classmethod
    def wrap(cls, func):
        signal = SyncSignal(func.__name__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            signal.dispatch_robust(*args, **kwargs)
            return result

        wrapper.subscribe = signal.subscribe
        wrapper.unsubscribe = signal.unsubscribe

        return wrapper


class AsyncSignal(BaseSingal[typing.Callable[..., typing.Awaitable[None]]]):

    async def dispatch(self, *args, **kwargs) -> None:
        for listener in self.listeners:
            await listener(*args, **kwargs)

    async def dispatch_robust(self, *args, **kwargs) -> None:
        try:
            await self.dispatch(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            _log.exception('Exception when processing signal %s: %s', self.name, exc)

    @classmethod
    def wrap(cls, func):
        signal = AsyncSignal(func.__name__)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await signal.dispatch_robust(*args, **kwargs)
            return result

        wrapper.subscribe = signal.subscribe
        wrapper.unsubscribe = signal.unsubscribe

        return wrapper


class SyncHook(BaseSingal[typing.Callable[..., typing.Any]]):

    def dispatch(self, *args, **kwargs) -> typing.Any:
        for listener in self.listeners:
            result = listener(*args, **kwargs)
            if result is not None:
                return result
        return None

    def dispatch_robust(self, *args, **kwargs) -> typing.Any:
        try:
            return self.dispatch(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            _log.exception('Exception when processing signal %s: %s', self.name, exc)


class AsyncHook(BaseSingal[typing.Callable[..., typing.Awaitable[typing.Any]]]):

    async def dispatch(self, *args, **kwargs) -> typing.Any:
        for listener in self.listeners:
            result = await listener(*args, **kwargs)
            if result is not None:
                return result
        return None

    async def dispatch_robust(self, *args, **kwargs) -> typing.Any:
        try:
            return await self.dispatch(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            _log.exception('Exception when processing signal %s: %s', self.name, exc)
        return None


def apply_signals(func):
    func._hermes_hooks_usage = True
    return func


class HermesSignalMetaclass(type):

    @staticmethod
    def wrap_with_function(func):

        before_signal = SyncSignal(f'before_{func.__name__}')
        after_signal = SyncSignal(f'after_{func.__name__}')

        @functools.wraps(func)
        def wrapper_function(*args, **kwargs):
            before_signal.dispatch(*args, **kwargs)
            result = func(*args, **kwargs)
            after_signal.dispatch(*args, **kwargs)
            return result

        wrapper_function.before = before_signal
        wrapper_function.after = after_signal

        return wrapper_function

    @staticmethod
    def wrap_with_coroutine(func):

        before_signal = AsyncSignal(f'before_{func.__name__}')
        after_signal = AsyncSignal(f'after_{func.__name__}')

        @functools.wraps(func)
        async def wrapper_function(*args, **kwargs):
            await before_signal.dispatch(*args, **kwargs)
            result = await func(*args, **kwargs)
            await after_signal.dispatch(*args, **kwargs)
            return result

        wrapper_function.before = before_signal
        wrapper_function.after = after_signal

        return wrapper_function

    def __new__(mcs, name, bases, namespace, **kwargs):

        for el_name in list(namespace.keys()):
            element = namespace[el_name]
            if getattr(element, '_hermes_hooks_usage', False):
                if inspect.iscoroutinefunction(element):
                    namespace[el_name] = HermesSignalMetaclass.wrap_with_coroutine(element)
                elif inspect.isfunction(element):
                    namespace[el_name] = HermesSignalMetaclass.wrap_with_function(element)
                else:
                    raise TypeError(f'_hermes_hooks_usage is unsupported for {element}')

        result = super().__new__(mcs, name, bases, namespace, **kwargs)

        return result
