import asyncio


__all__ = ('Vital',)


class Vital:

    def __init__(self, beat, save, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        self._beat = beat

        self._save = save

        self._delay = None

        self._acked = None

        self._paused = asyncio.Event(loop = loop)

        self._pulse = loop.create_task(self._start())

        self._loop = loop

    @property
    def paused(self):

        return self._paused

    @property
    def loop(self):

        return self._loop

    def ack(self):

        self._acked = True

    def inform(self, value):

        self._delay = value

    async def _sleep(self, checks = 2):

        last = checks - 1

        for index in range(checks):

            await self._paused.wait()

            if index == last:

                break

            await asyncio.sleep(self._delay)

    async def _start(self):

        while True:

            await self._sleep()

            if not self._acked:

                await self._save()

            self._acked = False

            await self._beat()

    def kill(self):

        self._pulse.cancel()

    def __repr__(self):

        state = (
            'dead'
            if self._pulse.cancelled()
            else 'alive'
            if self._paused.is_set()
            else 'paused'
        )

        return f'<{self.__class__.__name__} [{state}]>'
