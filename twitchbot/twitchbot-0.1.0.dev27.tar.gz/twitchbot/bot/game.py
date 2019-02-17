import twitchbot.api.game


class Game:
    def __init__(self, bot, game, api_game: twitchbot.api.game.Game = None):
        self._bot = bot
        self._game = game
        if api_game:
            self.set_game(api_game)

    async def init(self):
        self.set_game(await self._bot.api.game(self._game))

    def __getattr__(self, item):
        if hasattr(self._game, item):
            return getattr(self._game, item)

        raise AttributeError(f'Attribute {item} does not exist')

    def set_game(self, game: twitchbot.api.game.Game):
        self._game = game

    def is_api(self):
        return isinstance(self._game, twitchbot.api.game.Game)

    def __str__(self):
        if isinstance(self._game, twitchbot.api.game.Game):
            return str(self._game)
        return self._game

    def __int__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, Game) and other.id == self.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)
