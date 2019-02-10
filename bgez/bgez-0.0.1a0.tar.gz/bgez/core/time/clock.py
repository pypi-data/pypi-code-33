import time
import abc

__all__ = [
    'BaseClock',
    'TimeClock',
    'TickClock',
]

class BaseClock(abc.ABC):

    @abc.abstractmethod
    def time(self):
        '''Returns the time for this clock'''

    def tick(self):
        '''Updates the time if required, NO-OP by default.'''

class TimeClock(BaseClock):

    def time(self):
        return time.monotonic()

class TickClock(BaseClock):

    def __init__(self):
        self._counter = 0

    def time(self):
        return self._counter

    def tick(self):
        self._counter += 1
