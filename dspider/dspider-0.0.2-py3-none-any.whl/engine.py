# Standard Library
import asyncio
import logging

from typing import Optional, Type

# Local Folder
from .ctx import Context
from .httpclient import HTTPClient
from .middleware import Middleware, MiddlewareManager
from .spider import Spider, SpiderManager
from .typedefs import BaseFuture, BaseQueue, Loop, RequestQueue, ResponseQueue


__all__ = ("Engine",)
logger = logging.getLogger(__name__)


class Engine:
    def __init__(
        self,
        default_queue_class: Type[BaseQueue],
        default_httpclient_class: Type[HTTPClient],
        default_context_class: Type[Context],
        spider_manager_class: Type[SpiderManager],
        middleware_manager_class: Type[MiddlewareManager],
        *,
        loop: Optional[Loop] = None,
    ):
        self.loop = loop or asyncio.get_event_loop()

        self.req_spider_to_middleware: RequestQueue = default_queue_class(
            loop=self.loop
        )
        self.resp_httpclient_to_middleware: ResponseQueue = default_queue_class(
            loop=self.loop
        )
        self.req_middleware_to_httpclient: RequestQueue = default_queue_class(
            loop=self.loop
        )
        self.resp_middleware_to_spider: ResponseQueue = default_queue_class(
            loop=self.loop
        )
        self.httpclient: HTTPClient = default_httpclient_class(
            self.req_middleware_to_httpclient,
            self.resp_httpclient_to_middleware,
            loop=self.loop,
        )

        self.ctx = default_context_class()
        self.spider_manager = spider_manager_class(
            default_queue_class,
            self.req_spider_to_middleware,
            self.resp_middleware_to_spider,
            self.ctx,
            loop=self.loop,
        )
        self.middleware_manager = middleware_manager_class(
            queue_request=self.req_middleware_to_httpclient,
            queue_response=self.resp_middleware_to_spider,
            ctx=self.ctx,
            loop=self.loop,
        )
        self._dispatcher: Optional[BaseFuture] = None

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}()"

    @property
    def running(self) -> bool:
        return self._dispatcher is not None and not self._dispatcher.done()

    async def setup(self) -> None:
        logger.info(f"{self!r} setup")
        if self.running:
            raise RuntimeError(f"{self!r} is already running")

        await self.httpclient.setup()
        await self.middleware_manager.setup()
        await self.spider_manager.setup()

        self._dispatcher = asyncio.ensure_future(self.dispatch(), loop=self.loop)

    async def teardown(self) -> None:
        logger.info(f"{self!r} teardown")

        await self.spider_manager.teardown()
        await self.middleware_manager.teardown()
        await self.httpclient.teardown()

        if self._dispatcher is not None:
            self._dispatcher.cancel()
            await self._dispatcher

    async def add_spider(self, spider: Spider) -> None:
        await self.spider_manager.add(spider)

    async def join(self, spider: Optional[Spider] = None) -> None:
        await self.spider_manager.join(spider)

    async def add_middleware(self, middleware: Middleware) -> None:
        await self.middleware_manager.add(middleware)

    async def dispatch(self) -> None:
        try:
            await asyncio.gather(
                self.spider_to_middleware(),
                self.httpclient_to_middleware(),
                loop=self.loop,
            )
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.error(f"{self!r} dispatch exception", exc_info=True)

    async def spider_to_middleware(self) -> None:
        while True:
            request = await self.req_spider_to_middleware.get()
            self.middleware_manager.handle_request(request)

    async def httpclient_to_middleware(self) -> None:
        while True:
            resp_or_exc, request = await self.resp_httpclient_to_middleware.get()
            self.middleware_manager.handle_response(resp_or_exc, request)
