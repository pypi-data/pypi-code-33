from twitchbot.bot.context import Context


class Check:
    def __init__(self):
        self.description = f''

    async def check(self, ctx: Context):
        return True


class HasRank(Check):
    def __init__(self, rank):
        super().__init__()
        self._rank = rank
        self.description = f'rank {self._rank} is required'

    async def check(self, ctx: Context):
        return ctx.author.rank.has(self._rank)


class NotRank(HasRank):
    def __init__(self, rank):
        super().__init__(rank)
        self.description = f'rank {self._rank} is not allowed'

    async def check(self, ctx: Context):
        return not await super().check(ctx)


class MinRank(Check):
    def __init__(self, rank):
        super().__init__()
        self._rank = rank
        self.description = f'minimum rank {self._rank} is required'

    async def check(self, ctx: Context):
        return ctx.author.rank.has_power(ctx.author.rank.convert_rank(self._rank).power)


class IsOwner(Check):
    def __init__(self):
        super().__init__()
        self.description = f'you should be owner'

    async def check(self, ctx: Context):
        return ctx.author.login == ctx.bot.channel


class NotOwner(IsOwner):
    def __init__(self):
        super().__init__()
        self.description = f'you should not be owner'

    async def check(self, ctx: Context):
        return not await super().check(ctx)


class HasState(Check):
    def __init__(self, *states):
        super().__init__()
        self._states = states
        self.description = f'following state(s) should be true: {", ".join(self._states)}'

    async def check(self, ctx: Context):
        for state in self._states:
            if not ctx.bot.get_state(state, default=False):
                return False
        return True


class NotState(HasState):
    def __init__(self, *states):
        super().__init__(*states)
        self.description = f'following state(s) should be false: {", ".join(self._states)}'

    async def check(self, ctx: Context):
        return not await super().check(ctx)
