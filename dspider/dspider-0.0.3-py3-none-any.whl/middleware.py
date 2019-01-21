# Standard Library
import asyncio
import logging

from typing import Dict, Optional, Set

# Local Folder
from .ctx import Context
from .request import Request
from .spider import key_spider_count_of_processing_request
from .typedefs import (
    BaseFuture,
    Loop,
    RequestQueue,
    RequestQueueItem,
    ResponseQueue,
    ResponseQueueItem,
    RespOrExc,
)


__all__ = (
    "Middleware",
    "MiddlewareManager",
    "RedirectMiddleware",
    "ThrottleMiddleware",
)

logger = logging.getLogger(__name__)


class Middleware:
    name = "middleware_name"

    def __init__(self, *, loop: Loop = None) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self.queue_request: Optional[RequestQueue] = None
        self.queue_response: Optional[ResponseQueue] = None
        self.ctx: Optional[Context] = None
        self.is_running = False

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(name={self.name!r})"

    async def setup(
        self, queue_request: RequestQueue, queue_response: ResponseQueue, ctx: Context
    ) -> None:
        self.is_running = True
        self.queue_request = queue_request
        self.queue_response = queue_response
        self.ctx = ctx

    async def send_request(self, request: Request) -> None:
        if not self.is_running:
            raise RuntimeError(f"{self!r} is not running")

        assert self.ctx is not None
        spider_name = request.meta["spider"]
        key = key_spider_count_of_processing_request(spider_name)
        await self.ctx.incr(key)

        assert self.queue_request is not None
        await self.queue_request.put(request)

    async def send_response(self, resp_or_exc: RespOrExc, request: Request) -> None:
        if not self.is_running:
            raise RuntimeError(f"{self!r} is not running")

        assert self.ctx is not None
        spider_name = request.meta["spider"]
        key = key_spider_count_of_processing_request(spider_name)
        await self.ctx.incr(key)

        assert self.queue_response is not None
        await self.queue_response.put((resp_or_exc, request))

    async def teardown(self) -> None:
        pass

    async def handle_request(self, request: Request) -> Optional[RequestQueueItem]:
        return request

    async def handle_response(
        self, resp_or_exc: RespOrExc, request: Request
    ) -> Optional[ResponseQueueItem]:
        return resp_or_exc, request


class MiddlewareManager:
    def __init__(
        self,
        queue_request: RequestQueue,
        queue_response: ResponseQueue,
        ctx: Context,
        *,
        loop: Optional[Loop],
    ) -> None:
        self.running = False
        self.loop = loop or asyncio.get_event_loop()
        self.queue_response = queue_response
        self.queue_request = queue_request
        self.ctx = ctx

        self.middlewares: Dict[str, Middleware] = {}
        self.actions: Set[BaseFuture] = set()

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}()"

    async def setup(self) -> None:
        self.running = True
        for middleware in self.middlewares.values():
            await middleware.setup(self.queue_request, self.queue_response, self.ctx)

    async def teardown(self) -> None:
        self.running = False
        for middleware in self.middlewares.values():
            await middleware.teardown()

    async def add(self, middleware: Middleware) -> None:
        if self.running:
            raise RuntimeError(f"{self!r} is already running.")

        if middleware.name in self.middlewares:
            raise RuntimeError(f"{middleware!r} is already running.")

        self.middlewares[middleware.name] = middleware
        logger.debug(f"{self!r} add {middleware!r}")

    async def remove(self, middleware_name: str) -> None:
        pass

    async def _handle_request(self, request: Request) -> None:
        for middleware in self.middlewares.values():
            logger.debug(f"{self!r} handle request by {middleware!r}")
            try:
                rv = await middleware.handle_request(request)
                if rv is None:
                    spider_name = request.meta["spider"]
                    key = key_spider_count_of_processing_request(spider_name)
                    await self.ctx.decr(key)
                    return

                request = rv
            except asyncio.CancelledError:
                logger.warning(f"{self!r} handle request cancel at {middleware!r}")
                break
            except Exception:
                logger.error(f"{self!r} handle request exception by {middleware!r}")
        else:
            await self.queue_request.put(request)

    def handle_request(self, request: Request) -> None:
        logger.debug(f"{self!r} handle request ({request!r}))")
        fut = asyncio.ensure_future(self._handle_request(request), loop=self.loop)
        self.actions.add(fut)
        fut.add_done_callback(lambda x: self.actions.remove(x))

    async def _handle_response(self, resp_or_exc: RespOrExc, request: Request) -> None:
        middlewares = list(self.middlewares.values())
        for middleware in reversed(middlewares):
            logger.debug(f"{self!r} handle response by {middleware!r}")
            try:
                rv = await middleware.handle_response(resp_or_exc, request)
                if rv is None:
                    spider_name = request.meta["spider"]
                    key = key_spider_count_of_processing_request(spider_name)
                    await self.ctx.decr(key)
                    return

                resp_or_exc, request = rv
            except asyncio.CancelledError:
                logger.warning(f"{self!r} handle response cancel at {middleware!r}")
                break
            except Exception:
                logger.error(f"{self!r} handle response exception by {middleware!r}")
                break
        else:
            await self.queue_response.put((resp_or_exc, request))

    def handle_response(self, resp_or_exc: RespOrExc, request: Request) -> None:
        logger.debug(f"{self!r} handle response ({resp_or_exc!r}, {request!r})")
        fut = asyncio.ensure_future(
            self._handle_response(resp_or_exc, request), loop=self.loop
        )
        self.actions.add(fut)
        fut.add_done_callback(lambda x: self.actions.remove(x))


class RedirectMiddleware(Middleware):
    name = "redirect"


class DuplicatedRequestfilterMiddleware(Middleware):
    name = "duplicated_request_filter"


class ThrottleMiddleware(Middleware):
    name = "throttle"
