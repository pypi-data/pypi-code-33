import timeit
import numpy as np
from time import time as now


def time_once(code, n=1):
    ''' Measures execution time of code (best of 3).

    :param code: Code string or callable.
    :param n: Number of times to repeat execution (n x 3).

    :returns: The best execution time.
    '''
    times = min(timeit.Timer(code).repeat(3, n))

    return round(np.array(times)/n, 3)


class LRUCache():
    ''' Given a function and LRU caching implementation,
        caches the results of the function.

        :ivar impl: LRU cache implementation, for instance \
            functools.lru_cache.
        :ivar func: The function to cache.
        :ivar maxsize: The size of the cache.
        :ivar typed: Determines whether a distinction is \
            made between arguments of different types.
        :ivar cached: The cached function.
    '''
    def __init__(self, impl, func,
                 maxsize=128, typed=False):
        '''

        :param impl: LRU cache implementation, for instance \
            functools.lru_cache.
        :param func: The function to cache.
        :param maxsize: The size of the cache.
        :param typed: Determines whether a distinction is \
            made between arguments of different types.
        '''
        self.impl = impl
        self.func = func
        self.maxsize = maxsize
        self.typed = typed
        self.cached = None
        self.info = None

    def cache(self):
        ''' Caches the function.  '''
        self.cached = self.impl(self.maxsize,
                                self.typed)(self.func)

    def clear(self):
        ''' Clears the cache. '''
        if self.cached:
            self.cached.cache_clear()
            self.info = None

    def get_info(self):
        ''' Gets cache info. '''
        if self.cached:
            self.info = self.cached.cache_info()

    def hits_miss(self):
        ''' Calculates hits/miss ratio.
            In a muti-threaded environment, the calculation is approximate.

        :returns: The hits/miss ratio.
        '''
        if self.info is None:
            self.get_info()

        if self.info.misses == 0:
            return None

        return self.info.hits/self.info.misses


class StopWatch():
    ''' A simple stopwatch, which has a context manager.

    :ivar elapsed: Elapsed time in seconds.
    '''
    def __enter__(self):
        self.begin = now()
        self.elapsed = 0
        return self

    def __exit__(self, *args):
        self.elapsed = now() - self.begin
