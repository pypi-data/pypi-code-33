from typing import TypeVar as _TypeVar, Union as _Union, Awaitable as _Awaitable, cast as _cast

from inspect import isawaitable
from asyncio import sleep, gather
from asyncio import *

_T = _TypeVar('_T')
async def maybe_awaitable(value: _Union[_T, _Awaitable[_T]]) -> _T:
    if isawaitable(value):
        return await _cast(_Awaitable[_T], value)
    return _cast(_T, value)

from .deferred import *
from .task import *
from .task_manager import *
