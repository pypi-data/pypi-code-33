from typing import Callable, Tuple, Optional

__all__ = [
    'Timer',
    'TimeoutTimer',
    'IntervalTimer',
]

class Timer:

    __slots__ = ['_callback', '_deadline', '_cancelled']

    def __init__(self, deadline, callback, args, kargs):
        self._callback = callback, args, kargs
        self._deadline = deadline
        self._cancelled = False

    def __call__(self):
        if self._cancelled: return
        callback, args, kargs = self._callback
        callback(*args, **kargs)

    def __lt__(self, other):
        return False

    @property
    def deadline(self):
        return self._deadline

    @property
    def cancelled(self):
        return self._cancelled

    def cancel(self):
        self._cancelled = True

class TimeoutTimer(Timer):

    def __init__(self, clock: Callable, timeout, callback, args, kargs):
        super().__init__(max(timeout, 0) + clock(), callback, args, kargs)

class IntervalTimer(TimeoutTimer):

    __slots__ = ['_interval']

    def __init__(self, clock: Callable, interval, callback, args, kargs):
        super().__init__(clock, interval, callback, args, kargs)
        self._interval = interval

    def __call__(self):
        super().__call__()
        self._deadline += self._interval
        return self._deadline

    @property
    def interval(self):
        return self._interval
