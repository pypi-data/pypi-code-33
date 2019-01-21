# Standard Library
import asyncio
import logging

from collections import defaultdict
from functools import partial
from typing import (
    AsyncGenerator,
    Awaitable,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Optional,
    Set,
    Type,
)

# Local Folder
from .ctx import Context, Watcher
from .request import Request
from .response import Response
from .typedefs import (
    BaseCoroutine,
    BaseFuture,
    BaseQueue,
    KeyMaker,
    LifecyleAction,
    LifecyleActionReturn,
    Loop,
    RequestQueue,
    ResponseQueue,
    ResponseQueueItem,
    RespOrExc,
    WatcherChecker,
)


__all__ = (
    "Spider",
    "SpiderManager",
    "key_spider_count_of_processing_action",
    "key_spider_count_of_processing_request",
)
logger = logging.getLogger(__name__)


def key_spider_count_of_processing_request(spider_name: str) -> str:
    return f"SCOPR_{spider_name}"


def key_spider_count_of_processing_action(spider_name: str) -> str:
    return f"SCOPA_{spider_name}"


class Spider:
    name = "spider_name"

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(name={self.name!r})"

    async def setup(self) -> None:
        pass

    async def teardown(self) -> None:
        pass

    async def start_requests(self) -> LifecyleActionReturn:
        pass

    async def handle_response(
        self, response: Response, request: Request
    ) -> LifecyleActionReturn:
        pass

    async def handle_exc(
        self, exc: BaseException, request: Request
    ) -> LifecyleActionReturn:
        pass


class SpiderManager:
    def __init__(
        self,
        default_queue_class: Type[BaseQueue],
        queue_request: RequestQueue,
        queue_response: ResponseQueue,
        ctx: Context,
        *,
        loop: Optional[Loop] = None,
    ):
        self.loop = loop or asyncio.get_event_loop()

        self.queue_request = queue_request
        self.queue_response = queue_response
        self.ctx = ctx

        self.spiders: Dict[str, Spider] = {}
        self.spiders_queue_response: DefaultDict[str, ResponseQueue] = defaultdict(
            partial(default_queue_class, loop=self.loop)
        )
        self.lifecycles: Dict[str, BaseFuture] = {}
        self.actions: DefaultDict[str, Set[BaseFuture]] = defaultdict(set)
        self.watcher: Watcher = Watcher(
            checker=lambda: len(self.lifecycles) == 0, interval=0.1, loop=self.loop
        )
        self.watchers: Dict[str, Watcher] = {}

        self._dispatcher: Optional[BaseFuture] = None

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}()"

    async def setup(self) -> None:
        self._dispatcher = asyncio.ensure_future(
            self.dispatch_response(), loop=self.loop
        )

    async def teardown(self) -> None:
        if not self.running:
            raise RuntimeError(f"{self!r} is not running")

        if self._dispatcher is not None:
            self._dispatcher.cancel()

        if self.watcher.running:
            await self.watcher.stop()

        for watcher in self.watchers.values():
            if watcher.running:
                await watcher.stop()

    @property
    def running(self) -> bool:
        return self._dispatcher is not None and not self._dispatcher.done()

    async def dispatch_response(self) -> None:
        while True:
            item: ResponseQueueItem = await self.queue_response.get()
            req = item[1]
            spider_name = req.meta.get("spider", "")
            if spider_name not in self.spiders_queue_response:
                # for debug
                logger.warning(f"get unknown spider's response: spider={spider_name!r}")

            await self.spiders_queue_response[spider_name].put(item)

    async def add(self, spider: Spider) -> None:
        if not self.running:
            raise RuntimeError(f"{self!r} is not running")

        if spider.name in self.spiders:
            raise RuntimeError(f"{spider!r} is already running.")

        self.spiders[spider.name] = spider
        fut = self.lifecycles[spider.name] = asyncio.ensure_future(
            self.lifecycle(spider), loop=self.loop
        )

        def remove_from_lifecycles(fut: BaseFuture) -> None:
            del self.lifecycles[spider.name]

        fut.add_done_callback(remove_from_lifecycles)
        logger.debug(f"{self!r} add {spider!r}")

    async def join(self, spider: Optional[Spider] = None) -> None:
        if spider is None:
            watcher = self.watcher
        else:
            key = spider.name
            if key not in self.watchers:
                self.watchers[key] = Watcher(
                    checker=lambda: key not in self.lifecycles,
                    interval=0.1,
                    loop=self.loop,
                )

            watcher = self.watchers[key]

        if not watcher.running:
            await watcher.start()

        await watcher.join()

    async def remove(self, spider_name: str) -> None:
        pass

    async def incr(
        self,
        spider: Spider,
        key_maker: KeyMaker = key_spider_count_of_processing_request,
    ) -> None:
        await self.ctx.incr(key_maker(spider.name))

    async def decr(
        self,
        spider: Spider,
        key_maker: KeyMaker = key_spider_count_of_processing_request,
    ) -> None:
        await self.ctx.decr(key_maker(spider.name))

    def no_processing_request_checker(self, spider: Spider) -> WatcherChecker:
        key_scopr = key_spider_count_of_processing_request(spider.name)
        key_scopa = key_spider_count_of_processing_action(spider.name)

        async def checker() -> bool:
            return (await self.ctx.get(key_scopr, 0)) == 0 and (
                await self.ctx.get(key_scopa, 0)
            ) == 0

        return checker

    def should_exit(self, spider: Spider) -> None:
        self.lifecycles[spider.name].cancel()

    def handle_response_cb_maker(self, spider: Spider) -> Callable[[BaseFuture], None]:
        def handle_response_callback(fut: BaseFuture) -> None:
            asyncio.ensure_future(self.decr(spider), loop=self.loop)

        return handle_response_callback

    async def _send_request(self, request: Request, spider: Spider) -> None:
        request.meta["spider"] = spider.name
        await self.incr(spider)
        await self.queue_request.put(request)

    async def _handle_lifecycle_action(
        self, coro: LifecyleAction, spider: Spider
    ) -> None:
        if isinstance(coro, AsyncGenerator):
            async for req in coro:
                await self._send_request(req, spider)
        elif isinstance(coro, Awaitable):
            rv = await coro

            if rv is None:
                return

            if isinstance(rv, Request):
                await self._send_request(rv, spider)

            elif isinstance(rv, Iterable):
                for req in rv:
                    await self._send_request(req, spider)

    async def _handle_spider_action(self, spider: Spider, coro: BaseCoroutine) -> None:
        fut = asyncio.ensure_future(coro, loop=self.loop)
        await self.incr(spider, key_maker=key_spider_count_of_processing_action)
        actions = self.actions[spider.name]
        actions.add(fut)

        def cb(fut: BaseFuture) -> None:
            actions.remove(fut)
            asyncio.ensure_future(
                self.decr(spider, key_maker=key_spider_count_of_processing_action),
                loop=self.loop,
            )

        fut.add_done_callback(cb)
        await fut

    async def handle_start_requests(self, spider: Spider) -> None:
        logger.info(f"{spider!r} start_requests")

        try:
            coro = self._handle_lifecycle_action(spider.start_requests(), spider)
            await self._handle_spider_action(spider, coro)
        except Exception:
            logger.warning(f"{spider!r} start_requests error:", exc_info=True)

    async def handle_response(
        self, resp_or_exc: RespOrExc, request: Request, spider: Spider
    ) -> None:
        if isinstance(resp_or_exc, Response):
            if request.callback is not None:
                handler = getattr(spider, request.callback)
            else:
                handler = spider.handle_response
        else:
            handler = spider.handle_exc

        logger.debug(f"{spider!r} handle {resp_or_exc!r} by {handler!r}")
        try:
            coro = self._handle_lifecycle_action(handler(resp_or_exc, request), spider)
            await self._handle_spider_action(spider, coro)
        except Exception:
            logger.warning(f"{spider!r} start_requests error:", exc_info=True)

    async def lifecycle(self, spider: Spider) -> None:
        logger.info(f"{spider!r} setup")
        await spider.setup()
        watcher = Watcher(
            checker=self.no_processing_request_checker(spider),
            interval=0.1,
            loop=self.loop,
        )
        try:
            start_request_handler = asyncio.ensure_future(
                self.handle_start_requests(spider), loop=self.loop
            )
            queue = self.spiders_queue_response[spider.name]

            await watcher.register(partial(self.should_exit, spider))
            await watcher.start()
            while True:
                item: ResponseQueueItem = await queue.get()
                resp_or_exc, req = item
                logger.debug("receive %r from httpclient", resp_or_exc)
                asyncio.ensure_future(
                    self.handle_response(resp_or_exc, req, spider)
                ).add_done_callback(self.handle_response_cb_maker(spider))

        except asyncio.CancelledError:
            pass

        finally:
            await watcher.stop()
            logger.info(f"{spider!r} teardown")
            start_request_handler.cancel()
            try:
                await start_request_handler
            except asyncio.CancelledError:
                pass
            await spider.teardown()
