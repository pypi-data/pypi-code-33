import asyncio
import datetime
import weakref


class Interval:
    def __init__(self, func, timedelta: datetime.timedelta, wait_after: bool, *args, **kwargs):
        self.__name__ = func.__name__
        self.callback = func
        self.time_delta = timedelta
        self.wait_after = wait_after
        self.args = args
        self.kwargs = kwargs

        self.running = False

        self.enabled = self.kwargs.get('enabled', False)
        self.pass_context = self.kwargs.get('pass_context', True)

        try:
            self._checks = self.callback.__command_checks__
        except AttributeError:
            self._checks = []

    async def run(self, ctx):
        self.running = True
        while self.running:
            if not self.wait_after:
                await asyncio.sleep(self.time_delta.seconds)
            if await self.check(ctx):
                if self.pass_context:
                    if asyncio.iscoroutinefunction(self.callback):
                        await self.callback(ctx)
                    else:
                        self.callback(ctx)
                else:
                    if asyncio.iscoroutinefunction(self.callback):
                        await self.callback()
                    else:
                        self.callback()
            if self.wait_after:
                await asyncio.sleep(self.time_delta.seconds)

    async def check(self, ctx):
        for check in self._checks:
            if asyncio.iscoroutinefunction(check.check):
                if await check.check(ctx):
                    continue
            return False
        return True

    def set_check(self, *checks):
        self._checks = list(checks)

    def stop(self):
        self.running = False


class IntervalHandler:
    def __init__(self, ctx):
        self.context = ctx
        self._intervals = []

    async def start(self):
        for interval in self.context.bot.intervals:
            task = weakref.ref(asyncio.ensure_future(self.context.bot.intervals[interval].run(self.context)))
            self._intervals.append(task)

    async def stop(self):
        for interval in self._intervals:
            interval().cancel()
