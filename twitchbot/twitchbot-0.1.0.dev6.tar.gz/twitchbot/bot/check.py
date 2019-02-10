from twitchbot.bot.context import Context


class Check:
    async def check(self, ctx: Context):
        return True


class HasRank(Check):
    def __init__(self, rank):
        self._rank = rank

    async def check(self, ctx: Context):
        return ctx.author.rank.has(self._rank)


class NotRank(HasRank):
    async def check(self, ctx: Context):
        return not await super().check(ctx)


class IsOwner(Check):
    async def check(self, ctx: Context):
        return ctx.author.login == ctx.bot.channel


class NotOwner(IsOwner):
    async def check(self, ctx: Context):
        return not await super().check(ctx)


class HasState(Check):
    def __init__(self, *states):
        self._states = states

    async def check(self, ctx: Context):
        for state in self._states:
            if not ctx.bot.get_state(state):
                return False
        return True


class NotState(HasState):
    async def check(self, ctx: Context):
        return not await super().check(ctx)
