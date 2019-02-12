import logging
import aiohttp
import asyncio
import datetime

from .cache import Cache


class Client:
    BASE_URL: str = 'https://api.twitch.tv/helix/'
    COUNTER_MAX: int = 100
    TIMER_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=1)

    def __init__(self, client_id: str = None, token: str = None, cache: bool = True,
                 cache_duration: datetime.timedelta = None, loop=None):
        if not hasattr(self, 'log'):
            self.log = logging.getLogger(__name__)
        self.log.debug('Initialization complete')

        self._client_id = client_id
        self._token = token
        self._cache_enabled = cache
        self._event_loop = loop if loop is not None else asyncio.get_event_loop()

        self.session = aiohttp.ClientSession(loop=self._event_loop)
        self.user_cache = Cache(cache_duration)
        self.stream_cache = Cache(cache_duration)
        self.game_cache = Cache(cache_duration)
        self.last_use = None
        self.counter = 0
        self._unauthorized_callback = None

        self.BASE_URL = self.BASE_URL.rstrip('/')

    async def get(self, url, *args, **kwargs):
        if not self.last_use:
            self.last_use = datetime.datetime.now()
        if (self.last_use + self.TIMER_TIMEDELTA) > datetime.datetime.now() and self.counter >= self.COUNTER_MAX:
            await asyncio.sleep(((self.last_use + datetime.timedelta(minutes=1)) - datetime.datetime.now()).seconds)
            self.last_use = datetime.datetime.now()
            self.counter = 0
        self.counter += 1
        return await self.session.get(url, *args, **kwargs)

    async def put(self, url, *args, **kwargs):
        if not self.last_use:
            self.last_use = datetime.datetime.now()
        if (self.last_use + self.TIMER_TIMEDELTA) > datetime.datetime.now() and self.counter >= self.COUNTER_MAX:
            await asyncio.sleep(((self.last_use + datetime.timedelta(minutes=1)) - datetime.datetime.now()).seconds)
            self.last_use = datetime.datetime.now()
            self.counter = 0
        self.counter += 1
        return await self.session.put(url, *args, **kwargs)

    def set_token(self, token: str):
        self._token = token

    def cache_enabled(self):
        return self._cache_enabled

    def set_unauthorized_callback(self, func):
        if asyncio.iscoroutinefunction(func):
            self._unauthorized_callback = func

    async def _unauthorized(self):
        if self._unauthorized_callback:
            return await self._unauthorized_callback(self)
        else:
            raise UnauthorizedToken

    async def close(self):
        if self.session:
            await self.session.close()


class UnauthorizedToken(BaseException):
    pass
