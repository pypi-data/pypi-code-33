import functools
import logging
import time
import sys

from . import state

__all__ = [
    'Tracer', 'trace',
]

class Tracer:
    '''Trace calls to functions and log everything'''

    __slots__ = (
        'state',
        'logger',
        '_handler',
        '_formatter',
    )

    DEFAULT_RECORD_FORMAT = '[%(asctime)s] %(name)s:%(levelname)s:%(message)s'
    DEFAULT_DATE_FORMAT = '%H:%M:%S'

    def __init__(self, name: str = __name__, level: int = logging.DEBUG,
    format: str = DEFAULT_RECORD_FORMAT, datefmt: str = DEFAULT_DATE_FORMAT,
    enabled: bool = True):
        self.state = state.State(enabled)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._handler = logging.StreamHandler()
        self._formatter = logging.Formatter(fmt=format, datefmt=datefmt)
        self._handler.setFormatter(self._formatter)
        self.logger.addHandler(self._handler)

    @property
    def level(self): return self.logger.getLevel()
    @level.setter
    def level(self, lvl): self.logger.setLevel(lvl)

    @property
    def format(self): return self._formatter._fmt
    @format.setter
    def format(self, fmt): self._formatter._fmt = fmt

    @property
    def dateformat(self): return self._formatter.dateformat
    @dateformat.setter
    def dateformat(self, datefmt): self._formatter.datefmt = datefmt

    def trace(self, stack: bool = False, args: bool = False):
        def decorator(function: callable):
            @functools.wraps(function)
            def wrapper(*a, **b):
                if self.state: # passthrough
                    return function(*a, *b)

                message = f'calling {function}'
                if args:
                    message += f' with args:{a} kargs:{b}'
                self.logger.debug(message, stack_info=stack)

                start = time.monotonic()
                result = function(*a, **b)
                delta = time.monotonic() - start

                self.logger.debug('exited %s; it took: %ss', function, delta)
                return result
            return wrapper
        return decorator

_tracer = Tracer()
trace = _tracer.trace
