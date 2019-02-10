from typing import Iterator, Callable, Any

from time import time, sleep

def elapsed_time(function: Callable, *args, **kargs) -> (float, Any):
    '''Returns the time it took for function to be executed.'''
    old_time = time()
    result = function(*args, **kargs)
    return time() - old_time, result

def loopUntil(timeout: float, interval: float = None) -> Iterator:
    '''
    This is a generator that will sleep for `interval` seconds until `timeout`,
    seconds elapsed, returning the elapsed time after each iteration.

    ```py
    for elapsed in loopUntil(time, interval):
        print(elapsed)
    ```
    '''
    if (interval is not None) and (timeout < interval):
        raise ValueError(f'{timeout} < {interval}')
    start = time()
    yield 0
    while True:
        elapsed = time() - start # dt
        if interval is not None:
            sleep(max(min(interval, timeout - elapsed), 0))
        elapsed = time() - start # dt
        if elapsed >= timeout: return
        yield elapsed
