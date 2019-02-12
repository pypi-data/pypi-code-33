import asyncio


class Event:
    def __init__(self, func, *args, **kwargs):
        self.__name__ = func.__name__
        self.callback = func
        self.args = args
        self.kwargs = kwargs

        self.enabled = self.kwargs.get('enabled', False)
        self.pass_context = self.kwargs.get('pass_context', True)

    async def __call__(self, ctx=None, *args, **kwargs):
        if self.pass_context:
            if asyncio.iscoroutinefunction(self.callback):
                return await self.callback(ctx, *args, **kwargs)
            else:
                return self.callback(ctx, *args, **kwargs)
        else:
            if asyncio.iscoroutinefunction(self.callback):
                return await self.callback(*args, **kwargs)
            else:
                return self.callback(*args, **kwargs)