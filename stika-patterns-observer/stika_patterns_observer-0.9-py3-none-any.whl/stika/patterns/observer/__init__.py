import typing
import typing_extensions as typing_ext


T = typing.TypeVar('T')


class Observer(typing_ext.Protocol[T]):
    def notify(self, event: T): ...


class Observable(typing_ext.Protocol[T]):
    def register(self, observer: Observer[T]): ...

    def unregister(self, observer: Observer[T]): ...


class LambdaObserver(typing.Generic[T]):

    __slots__ = ["_func"]

    def __init__(self, func: typing.Callable[[T], None]):
        self._func = func

    def notify(self, event: T):
        self._func(event)


class AbstractObservable(typing.Generic[T]):

    __slots__ = ["_observers"]

    _observers: typing.List[Observer[T]]

    def __init__(self):
        self._observers = list()

    def register(self, receiver: Observer[T]):
        self._observers.append(receiver)

    def unregister(self, receiver: Observer[T]):
        self._observers.remove(receiver)

    def _notify_observers(self, event: T):
        for observer in self._observers:
            observer.notify(event)
