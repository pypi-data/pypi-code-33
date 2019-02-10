from typing import TypeVar, Callable, Awaitable

import functools
import asyncio

__all__ = [
    'task'
]

RT = TypeVar('RT')

def task(function: Callable[..., Awaitable[RT]]) -> Callable[..., Awaitable[RT]]:
    '''
    Automatically register a task in the eventloop on function call.
    '''
    if not asyncio.iscoroutinefunction(function):
        function = asyncio.coroutine(function)

    @functools.wraps(function)
    def wrapper(*args, **kargs) -> Awaitable[RT]:
        return asyncio.ensure_future(function(*args, **kargs))
    return wrapper
