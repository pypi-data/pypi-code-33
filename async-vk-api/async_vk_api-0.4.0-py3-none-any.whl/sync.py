from contextlib import asynccontextmanager

import trio


class Throttler:

    def __init__(self, rate):
        self.rate = rate
        # Using binary `trio.Semaphore` instead of `trio.Lock`
        # to be able to release it from the child task.
        self._sema = trio.Semaphore(1)

    @asynccontextmanager
    async def __call__(self):
        await self._sema.acquire()
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._tick)
            yield

    async def _tick(self):
        await trio.sleep(self.rate)
        self._sema.release()

    @property
    def locked(self):
        return not self._sema.value
