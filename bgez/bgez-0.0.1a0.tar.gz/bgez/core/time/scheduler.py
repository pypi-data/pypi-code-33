from typing import Union, List, Tuple, Callable

from .timer import Timer, TimeoutTimer, IntervalTimer
from .clock import BaseClock

import heapq

__all__ = [
    'Scheduler'
]

class Scheduler:

    def __init__(self, clock: BaseClock):
        self._timers: List[Tuple[Union[int, float], Timer]] = []
        self._clock = clock

    def __call__(self) -> None:
        '''
        Returns the state of the PriorityQueue, True if empty, else False.
        '''
        timers = self._timers
        while timers and timers[0][0] <= self._clock.time():
            timer = timers[0][1]
            deadline = timer()
            if deadline is None:
                heapq.heappop(timers)
            else:
                heapq.heapreplace(timers, (deadline, timer))

    def timeout(self, timeout, callback: Callable, *args, **kargs) -> Timer:
        '''Execute a callback after a given amount of time.'''
        timer = TimeoutTimer(self._clock.time, timeout, callback, args, kargs)
        heapq.heappush(self._timers, (timer.deadline, timer))
        return timer

    def interval(self, interval, callback: Callable, *args, **kargs) -> Timer:
        '''Repeat a callback periodically over time.'''
        timer = IntervalTimer(self._clock.time, interval, callback, args, kargs)
        heapq.heappush(self._timers, (timer.deadline, timer))
        return timer

    def tick(self):
        self._clock.tick()
        self()

    @property
    def value(self):
        return self._clock.time()
