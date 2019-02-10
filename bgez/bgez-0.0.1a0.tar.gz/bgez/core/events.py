from typing import Any, TypeVar, Optional, Union, Callable, Hashable, Iterable

import abc

from collections import OrderedDict, defaultdict

from bgez import logger

__all__ = [
    'BaseSubject', 'Subject',
    'BaseEventEmitter', 'EventEmitter',
]

Callback = TypeVar('Callback', bound=Callable[..., Any])
Decorator = Callable[[Callback], Callback]

class BaseSubject(abc.ABC):

    @abc.abstractmethod
    def subscribe(self, callback: Callback = None, *, once: bool = True) -> Union[Decorator, None]:
        '''Subscribes `callback` to this subject.'''

    @abc.abstractmethod
    def notify(self, *args: Any, catch: bool = True) -> int:
        '''Notifies the `callbacks` for this subject.'''

    @abc.abstractmethod
    def unsubscribe(self, handle: Any) -> None:
        '''Unsubscribes `callback` from this subject.'''

    @property
    @abc.abstractmethod
    def subscribers(self) -> Iterable:
        '''Returns the list of subscribers for this subject.'''

    @abc.abstractmethod
    def clear(self) -> None:
        '''Clears every callback from this subject.'''

    @abc.abstractmethod
    def __len__(self) -> int:
        '''Returns the number of callbacks registered to this subject.'''

    @abc.abstractmethod
    def __contains__(self, handle: Any) -> bool:
        '''Returns if the handle is registered to this subject.'''

class BaseEventEmitter(abc.ABC):

    @property
    @abc.abstractmethod
    def events(self) -> Iterable[str]:
        '''Returns the current list of available events.'''

    @abc.abstractmethod
    def subject(self, subject: Hashable) -> BaseSubject:
        '''Returns the given `subject`.'''

    @abc.abstractmethod
    def any(self, callback: Callable) -> Callable:
        '''Registers `callback` to be called for any emit.'''

    @abc.abstractmethod
    def on(self, subject: Hashable, callback: Callable) -> Callable:
        '''Registers `callback` to be called on `subject`.'''

    @abc.abstractmethod
    def once(self, subject: Hashable, callback: Callable) -> Callable:
        '''Registers `callback` to be called on `subject` only once.'''

    @abc.abstractmethod
    def remove(self, subject: Hashable, handle: Any) -> None:
        '''Unregisters `callback` from `subject`.'''

    @abc.abstractmethod
    def emit(self, subject: Hashable, *args: Any, catch: bool = True) -> int:
        '''
        Emits event for `subject` with `args`, blocks the thread.
        Returns the number of callbacks that were called.
        '''

    @abc.abstractmethod
    def listeners(self, subject: Hashable) -> Iterable:
        '''Returns the list of listeners for `subject`.'''

    @abc.abstractmethod
    def clear(self, subject: Hashable) -> None:
        '''Clears `subject`.'''

    @abc.abstractmethod
    def clear_all(self) -> None:
        '''Clears every subject.'''

    @abc.abstractmethod
    def __contains__(self, subject: Hashable) -> bool:
        '''Returns if `subject` is a valid event for this emitter.'''

class Subject(BaseSubject):

    def __init__(self):
        self.__callbacks = OrderedDict()

    def subscribe(self, callback: Optional[Callable] = None, *, once: bool = False) -> Optional[Decorator]:
        def decorator(callback: Callable):
            subscriber = callback
            handle = callback
            if once:
                def subscriber(*args: Any, **kargs: Any): # pylint: disable=E0102
                    self.unsubscribe(callback)
                    callback(*args, **kargs)
            self.__callbacks[handle] = subscriber
        if callback is None:
            return decorator
        decorator(callback)
        return None

    def unsubscribe(self, handle: Any) -> None:
        self.__callbacks.pop(handle, None)

    def notify(self, *args, catch: bool = True) -> int:
        callbacks = [*self.__callbacks.values()] # copy
        size = len(callbacks)

        if catch: self._try_exec(callbacks, args)
        else: self._exec(callbacks, args)

        return size

    def _try_exec(self, callbacks, args):
        for callback in callbacks:
            try:
                callback(*args)
            except Exception as e:
                logger.exception("", exc_info=e)

    def _exec(self, callbacks, args):
        for callback in callbacks:
            callback(*args)

    @property
    def subscribers(self) -> Iterable:
        return list(self.__callbacks.keys())

    def clear(self) -> None:
        self.__callbacks.clear()

    def __len__(self) -> int:
        return len(self.__callbacks)

    def __contains__(self, handle: Any) -> bool:
        return handle in self.__callbacks

class EventEmitter(BaseEventEmitter):
    __Subject__ = Subject

    def __init__(self, events: Iterable = None):
        self.__any = self.__Subject__()
        self.__subjects: dict = defaultdict(self.__Subject__)
        self.__valid_subjects = set(events) if events else None

    def __check_subject(self, subject: Hashable) -> None:
        if subject not in self:
            raise AttributeError(f'no subject named "{subject}"')

    @property
    def events(self):
        subjects = self.__valid_subjects
        return tuple(self.__subjects.keys() if subjects is None else subjects)

    def subject(self, subject: Hashable) -> BaseSubject:
        self.__check_subject(subject)
        return self.__subjects[subject]

    def any(self, callback: Callable = None, *, once: bool = False):
        return self.__any.subscribe(callback, once=once)

    def on(self, subject: Hashable, callback: Callable = None, **kargs) -> Any:
        self.__check_subject(subject)
        return self.__subjects[subject].subscribe(callback, **kargs)

    def once(self, subject: Hashable, callback: Callable = None, **kargs) -> Any:
        self.__check_subject(subject)
        return self.on(subject, callback, **kargs, once=True)

    def remove(self, subject: Hashable, handle: Any) -> None:
        self.__check_subject(subject)
        self.__subjects[subject].unsubscribe(handle)

    def emit(self, subject: Hashable, *args: Any, catch: bool = True) -> int:
        self.__check_subject(subject)
        self.__any.notify(subject, *args, catch=catch)
        return self.__subjects[subject].notify(*args)

    def listeners(self, subject: Hashable) -> Iterable:
        self.__check_subject(subject)
        return self.__subjects[subject].subscribers

    def clear(self, subject: Hashable) -> None:
        self.__clear_subject(subject)

    def clear_all(self):
        for subject in self.events:
            self.clear(subject)

    def __clear_subject(self, subject: Hashable):
        self.__check_subject(subject)
        if subject in self.__subjects:
            _subject = self.__subjects.pop(subject)
            _subject.clear()

    def __contains__(self, subject: Hashable) -> bool:
        return (self.__valid_subjects is None) or (subject in self.__valid_subjects)
