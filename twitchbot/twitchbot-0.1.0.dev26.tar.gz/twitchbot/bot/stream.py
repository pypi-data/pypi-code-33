import twitchbot.api.stream


class Stream:
    def __init__(self, bot, stream, api_stream: twitchbot.api.stream.Stream = None):
        self._bot = bot
        self._stream = stream
        if api_stream:
            self.set_stream(api_stream)

    async def init(self):
        self.set_stream(await self._bot.api.stream(self._stream))
        if isinstance(self._stream, twitchbot.api.stream.Stream):
            self._stream.game = await self._bot.api.game(self._stream.game_id)

    def is_api(self):
        return isinstance(self._stream, twitchbot.api.stream.Stream)

    @property
    def live(self) -> bool:
        if isinstance(self._stream, twitchbot.api.stream.Stream):
            return self._stream.live
        else:
            return False

    def __getattr__(self, item):
        if hasattr(self._stream, item):
            return getattr(self._stream, item)

        raise AttributeError(f'Attribute {item} does not exist')

    def set_stream(self, stream: twitchbot.api.stream.Stream):
        self._stream = stream

    def __str__(self):
        if isinstance(self._stream, twitchbot.api.stream.Stream):
            return self._stream.user_display_name
        return self._stream
