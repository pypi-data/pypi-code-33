import asyncio


def aioeachlimit(seq, coro, concurrency_limit, *, discard_results=False):
    if isinstance(seq, asyncio.Queue):
        return _AioEachLimitQueue(seq, coro, concurrency_limit, discard_results)
    else:
        return _AioEachLimitSeq(seq, coro, concurrency_limit, discard_results)


class _AioEachLimit():

    def __init__(self, seq, coro, concurrency_limit, discard_results=False):
        self._seq = seq
        self._coro = coro
        self._limit = concurrency_limit
        self._discard_results = discard_results

        self._completed = asyncio.Queue()
        self._pending = 0
        self._processed = 0

        self._completion_handler_task = asyncio.create_task(self._completion_handler())
        self._can_queue_next = asyncio.Event()
        self._can_yield_result = asyncio.Event()

    @property
    def count_processed(self):
        return self._processed

    async def wait(self):
        return await self._completion_handler_task

    async def _run_next(self):
        try:
            item = await self._get_next_item()
            result = await self._coro(item)

            if not self._discard_results:
                await self._completed.put(result)

            self._processed += 1
        except _OutOfItems:
            pass

        self._pending -= 1
        self._can_queue_next.set()
        self._can_yield_result.set()

    async def _completion_handler(self):
        for _ in range(self._limit):
            self._pending += 1
            asyncio.shield(self._run_next())

        while self._pending > 0:
            await self._can_queue_next.wait()
            self._can_queue_next.clear()

            while self._pending < self._limit and self._has_next_item():
                self._pending += 1
                asyncio.shield(self._run_next())

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            if not self._completed.empty():
                return self._completed.get_nowait()

            if self._completion_handler_task.done():
                raise StopAsyncIteration

            await self._can_yield_result.wait()
            self._can_yield_result.clear()


class _AioEachLimitSeq(_AioEachLimit):

    def __init__(self, *args, **kwargs):
        self._i = 0
        super().__init__(*args, **kwargs)

    def _has_next_item(self):
        return self._i < len(self._seq)

    async def _get_next_item(self):
        if not self._has_next_item():
            raise _OutOfItems

        next_item = self._seq[self._i]
        self._i += 1

        return next_item


class _AioEachLimitQueue(_AioEachLimit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _has_next_item(self):
        return True

    async def _get_next_item(self):
        return await self._seq.get()


class _OutOfItems(Exception):
    pass
