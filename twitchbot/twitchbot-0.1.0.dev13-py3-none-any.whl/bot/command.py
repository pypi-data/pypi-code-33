import asyncio
import inspect

from twitchbot.bot.context import Context


class Command:
    def __init__(self, func, *args, **kwargs):
        self.__name__ = func.__name__
        self.callback = func
        self.args = args
        self.kwargs = kwargs

        self.name = self.kwargs.get('name', func.__name__)
        if not self.name:
            self.name = func.__name__
        self.aliases = self.kwargs.get('aliases', [])
        self.prefix = self.kwargs.get('prefix', None)
        self.enabled = self.kwargs.get('enabled', False)
        self.pass_context = self.kwargs.get('pass_context', True)
        self.help = self.kwargs.get('help', [])

        if len(self.help) == 0:
            parameters = self.parameters

            for param in parameters:
                if issubclass(parameters[param].annotation, Context):  # Skip Context parameter
                    continue
                self.help.append(parameters[param].annotation)

        try:
            self._checks = self.callback.__command_checks__
        except AttributeError:
            self._checks = []

    @property
    def parameters(self):
        obj = self.callback
        signature = inspect.signature(obj)
        parameters = signature.parameters.copy()

        return parameters

    async def check(self, ctx: Context, dry: bool = False):
        for check in self._checks:
            if asyncio.iscoroutinefunction(check.check):
                result = await check.check(ctx)
                if result:
                    continue
                else:
                    if not dry:  # On dry run, we don't output
                        await ctx.send(f'Failed command requirement: {check.description}')
            return False
        return True

    def set_check(self, *checks):
        self._checks = list(checks)

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
