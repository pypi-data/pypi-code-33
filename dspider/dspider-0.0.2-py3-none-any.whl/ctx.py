# Standard Library
import asyncio
import logging

from abc import abstractmethod
from typing import Any, Dict, Optional, Set

# Local Folder
from .typedefs import (
    AsyncStrIterable,
    BaseFuture,
    Loop,
    WatcherCallback,
    WatcherChecker,
)
from .utils import sentinel


__all__ = ("Watcher", "AbstractContext", "Context", "RedisContext")
logger = logging.getLogger(__name__)


class Watcher:
    def __init__(
        self, checker: WatcherChecker, interval: float, *, loop: Optional[Loop] = None
    ):
        self.loop = loop or asyncio.get_event_loop()

        self.checker = checker
        self.interval = interval
        self._cronjob: Optional[BaseFuture] = None

        self.cbs: Set[WatcherCallback] = set()
        self.running: bool = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(checker={self.checker!r},interval={self.interval!r})"

    async def handle_cbs(self) -> None:
        logger.debug(f"{self!r} executing callback")
        for cb in self.cbs:
            try:
                none_or_coro = cb()
                if none_or_coro is not None:
                    await none_or_coro

            except Exception:
                logger.warning(f"{self!r} callback exception by {cb!r}", exc_info=True)

    async def _runner(self) -> None:
        while True:
            await asyncio.sleep(self.interval)
            checked = False

            try:
                checked_or_coro = self.checker()
                if isinstance(checked_or_coro, bool):
                    checked = checked_or_coro
                else:
                    checked = await checked_or_coro
            except Exception:
                logger.warning(
                    f"{self!r} checker exception by {self.checker}", exc_info=True
                )

            if checked:
                await self.handle_cbs()

    async def start(self) -> None:
        self.running = True
        await self.cronjob_run_or_stop()

    async def cronjob_run_or_stop(self) -> None:
        if self.running and len(self.cbs) > 0:
            if self._cronjob is None or self._cronjob.done():
                self._cronjob = asyncio.ensure_future(self._runner(), loop=self.loop)
        elif self._cronjob is not None:
            self._cronjob.cancel()

            try:
                await self._cronjob
            except asyncio.CancelledError:
                pass

            self._cronjob = None

    async def stop(self) -> None:
        if not self.running:
            raise RuntimeError(f"{self!r} is not running")

        self.running = False
        await self.cronjob_run_or_stop()

    async def register(self, cb: WatcherCallback) -> None:
        self.cbs.add(cb)
        await self.cronjob_run_or_stop()

    async def unregister(self, cb: WatcherCallback) -> None:
        self.cbs.remove(cb)
        await self.cronjob_run_or_stop()

    async def join(self) -> None:
        waiter: BaseFuture = asyncio.Future()

        def not_wait() -> None:
            waiter.set_result(None)
            asyncio.ensure_future(self.unregister(not_wait), loop=self.loop)

        await self.register(not_wait)

        await waiter


class AbstractContext(AsyncStrIterable):
    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """ set the value of key """

    @abstractmethod
    async def get(self, key: str, default: Any = sentinel) -> Any:
        """ get the value of key """

    @abstractmethod
    async def incr(self, key: str, num: int = 1) -> int:
        """ increase the number of key """

    @abstractmethod
    async def decr(self, key: str, num: int = 1) -> int:
        """ decrease the number of key """


class Context(AbstractContext):
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    async def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    async def get(self, key: str, default: Any = sentinel) -> Any:
        if key not in self._store:
            if default is not sentinel:
                return default
            else:
                raise KeyError(f"{key!r} notfound.")

        return self._store[key]

    async def incr(self, key: str, num: int = 1) -> int:
        self._store[key] = self._store.setdefault(key, 0) + num
        return self._store[key]

    async def decr(self, key: str, num: int = 1) -> int:
        return await self.incr(key, -num)

    def __aiter__(self) -> "Context":
        if hasattr(self, "_keys"):
            delattr(self, "_keys")

        return self

    async def __anext__(self) -> str:
        if not hasattr(self, "_keys"):
            self._keys = iter(self._store.keys())

        return next(self._keys)


class RedisContext(AbstractContext):
    # https://redis.io/topics/notifications
    pass
