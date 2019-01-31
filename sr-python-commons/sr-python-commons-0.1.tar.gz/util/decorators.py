import functools
import time
import traceback
import hashlib
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, timedelta
import inspect


def autoargs(fun):  # automatically assign args
    def autoargs(*include, **kwargs):
        def _autoargs(func):
            attrs, varargs, varkw, defaults = inspect.getargspec(func)

            def sieve(attr):
                if kwargs and attr in kwargs['exclude']:
                    return False
                if not include or attr in include:
                    return True
                else:
                    return False

            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                # handle default values
                if defaults:
                    for attr, val in zip(reversed(attrs), reversed(defaults)):
                        if sieve(attr):
                            setattr(self, attr, val)
                # handle positional arguments
                positional_attrs = attrs[1:]
                for attr, val in zip(positional_attrs, args):
                    if sieve(attr):
                        setattr(self, attr, val)
                # handle varargs
                if varargs:
                    remaining_args = args[len(positional_attrs):]
                    if sieve(varargs):
                        setattr(self, varargs, remaining_args)
                # handle varkw
                if kwargs:
                    for attr, val in kwargs.items():
                        if sieve(attr):
                            setattr(self, attr, val)
                return func(self, *args, **kwargs)

            return wrapper

        return _autoargs


class Cached:  # sample usage: @Cached(duration=timedelta(days=1))
    def __init__(self, *args, **kwargs):
        self.cached_function_responses = {}
        self.duration = kwargs.get("duration", timedelta(seconds=0))

    def __call__(self, func):
        def inner(*args, **kwargs):
            if not self.duration or func not in self.cached_function_responses or (
                    datetime.now() - self.cached_function_responses[func]['fetch_time'] > self.duration):
                if 'duration' in kwargs: del kwargs['duration']
                res = func(*args, **kwargs)
                self.cached_function_responses[func] = {'data': res, 'fetch_time': datetime.now()}
            return self.cached_function_responses[func]['data']

        return inner


def retry(ExceptionToCheck, retry=3, delay=3, backoff=2, logger=None, default_result=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param retry: number of times to try (not retry) before giving up
    :type retry: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = retry, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if default_result:
                return default_result
            else:
                return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
