# Standard Library
import asyncio

from collections.abc import AsyncIterable
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Iterable, Tuple, Union

# Third Party Library
from aiohttp.typedefs import LooseCookies as Cookies
from aiohttp.typedefs import LooseHeaders as Headers

# Local Folder
from .queue import Queue
from .request import Request
from .response import Response


BaseCoroutine = Coroutine[Any, Any, None]
BoolCoroutine = Coroutine[Any, Any, bool]
KeyMaker = Callable[[str], str]
Loop = asyncio.AbstractEventLoop
RequestQueueItem = Request
RespOrExc = Union[Response, BaseException]
ResponseQueueItem = Tuple[RespOrExc, Request]
WatcherCallback = Callable[[], Union[None, BaseCoroutine]]
WatcherChecker = Callable[[], Union[bool, BoolCoroutine]]

if TYPE_CHECKING:  # pragma: no cover
    ResponseQueue = Queue[ResponseQueueItem]
    RequestQueue = Queue[RequestQueueItem]
    BaseQueue = Queue[Any]
    FutureReturnResponse = asyncio.Future[Response]
    AsyncStrIterable = AsyncIterable[str]
    AsyncRequestIterable = AsyncIterable[Request]
    BaseFuture = asyncio.Future[None]
else:
    BaseQueue = ResponseQueue = RequestQueue = Queue
    FutureReturnResponse = BaseFuture = asyncio.Future
    AsyncRequestIterable = AsyncStrIterable = AsyncIterable

LifecyleActionReturn = Union[Request, Iterable[Request], AsyncRequestIterable]
LifecyleAction = Coroutine[None, None, LifecyleActionReturn]

__all__ = (
    "AsyncRequestIterable",
    "AsyncStrIterable",
    "BaseCoroutine",
    "BaseFuture",
    "BaseQueue",
    "BoolCoroutine",
    "Cookies",
    "FutureReturnResponse",
    "Headers",
    "KeyMaker",
    "LifecyleAction",
    "LifecyleActionReturn",
    "RequestQueue",
    "RequestQueueItem",
    "RespOrExc",
    "ResponseQueue",
    "ResponseQueueItem",
    "WatcherCallback",
    "WatcherChecker",
)
