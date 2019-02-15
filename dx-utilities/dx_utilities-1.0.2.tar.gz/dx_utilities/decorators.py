# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""General-use function decorators"""
from functools import wraps


def tolerate_input(*args, cast=float):
    """Decorator that tries to cast the specified
    ``*args`` into the designated type before
    calling the wrapped function.

    :param \*args: Names of the input arguments
        to allow for the tolerance.
    :param cast: The type to cast the args.
    """

    def decorator(method):

        @wraps(method)
        def wrapper(*args2, **kwargs):
            for arg in args:
                if kwargs.get(arg):
                    kwargs[arg] = cast(kwargs[arg])

            return method(*args2, **kwargs)

        return wrapper

    return decorator
