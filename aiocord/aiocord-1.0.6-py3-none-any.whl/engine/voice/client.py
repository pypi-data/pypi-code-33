import asyncio
import aiocord
import collections
import functools

from . import helpers


__all__ = ('Client',)


class Client:

    __slots__ = ('_cache', '_events', '_tracks', '_loop')

    def __init__(self, cache, loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        self._cache = cache

        self._events = helpers.events_from_client(self)

        self._tracks = collections.defaultdict(list)

        self._loop = loop

    def attach(self, voice):

        callback = functools.partial(self._callback, voice)

        voice.track(callback)

    def track(self, name):

        def decorator(function):

            def wrapper(*args):

                return function(*args)

            self._tracks[name].append(wrapper)

            return wrapper

        return decorator

    def check(self, name):

        value = asyncio.Event(loop = self._loop)

        def decorator(function):

            callbacks = self._tracks[name]

            async def callback(*args):

                if not await function(*args):

                    return

                value.set()

            callbacks.append(callback)

            async def observe():

                await value.wait()

                callbacks.remove(callback)

            coroutine = observe()

            self._loop.create_task(coroutine)

            return value

        return decorator

    async def _dispatch(self, name, values):

        callbacks = self._tracks[name]

        coroutines = (callback(*values) for callback in callbacks)

        await asyncio.gather(*coroutines, loop = self._loop)

    def _callback(self, voice, data):

        name = 'SPEAKING'

        event = self._events[name]

        coroutine = event(voice, data)

        self._loop.create_task(coroutine)

    def _break(self, data):

        user_id = data['user_id']

        ssrc = data['ssrc']

        state = data['speaking']

        return user_id, ssrc, state

    def _handle(self, data):

        user_id, ssrc, state = self._break(data)

        return user_id, ssrc, state

    async def speaking(self, voice, data):

        user_id, ssrc, state = self._handle(data)

        guild, member = self._cache(voice.guild_id, user_id)

        values = (voice, guild, member, ssrc, state)

        await self._dispatch('speaking', values)
