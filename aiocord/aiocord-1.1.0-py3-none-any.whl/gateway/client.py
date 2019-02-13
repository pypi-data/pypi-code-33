import asyncio
import aiohttp
import yarl
import enum
import zlib
import json
import random
import os

from . import errors
from . import vital


__all__ = ('Client',)


class OpCode(enum.IntEnum):

    dispatch = 0
    heartbeat = 1
    identify = 2
    status_update = 3
    voice_state_update = 4
    voice_server_ping = 5
    resume = 6
    reconnect = 7
    request_guild_members = 8
    invalid_session = 9
    hello = 10
    heartbeat_ack = 11


async def inspect():

    return ({}, 250)


async def determine():

    return (60, 1)


class Client:

    __slots__ = ('_token', '_info', '_url', '_saving', '_vital',  '_inspect',
                 '_determine', '_websocket', '_flow', '_buffer', '_inflator',
                 '_sequence', '_session_id', '_greeting', '_callbacks',
                 '_session', '_loop', '_closed')

    _suffix = b'\x00\x00\xff\xff'

    _query = {
        'v': 7,
        'encoding': 'json',
        'compress': 'zlib-stream'
    }

    def __init__(self,
                 session,
                 token,
                 info,
                 inspect = inspect,
                 determine = determine,
                 loop = None):

        if not loop:

            loop = asyncio.get_event_loop()

        self._info = info

        self._token = token

        self._url = None

        saving = asyncio.Event(loop = loop)

        saving.set()

        self._saving = saving

        self._vital = vital.Vital(self._heartbeat, self._save)

        self._inspect = inspect

        self._determine = determine

        self._websocket = None

        self._flow = None

        self._buffer = bytearray()

        self._inflator = None

        self._sequence = None

        self._session_id = None

        self._greeting = asyncio.Event(loop = loop)

        self._callbacks = []

        self._session = session

        self._loop = loop

        self._closed = False

    @property
    def info(self):

        return self._info

    @property
    def closed(self):

        return self._closed

    def track(self, callback):

        self._callbacks.append(callback)

    def update(self, url):

        self._url = yarl.URL(url).with_query(self._query)

    def patch(self, value):

        self._session_id = value

    __payload = ('op', 'd', 's', 't')

    @staticmethod
    def _build(code, data, *rest, keys = __payload):

        values = (code, data, *rest)

        payload = dict(zip(keys, values))

        return payload

    @staticmethod
    def _break(payload, keys = __payload):

        values = tuple(map(payload.get, keys))

        return values

    async def _push(self, *values):

        payload = self._build(*values)

        await self._websocket.send_json(payload)

    async def _pull(self, payload):

        (code, data, sequence, name) = self._break(payload)

        try:

            marker = OpCode(code)

        except ValueError:

            return

        if marker is OpCode.dispatch:

            self._sequence = sequence

            for callback in self._callbacks:

                callback(name, data)

            return

        if marker is OpCode.heartbeat:

            await self._heatbeat()

            return

        if marker is OpCode.heartbeat_ack:

            self._vital.ack()

            return

        if marker is OpCode.reconnect:

            await self._engage(False)

            return

        if marker is OpCode.invalid_session:

            if data:

                delay = random.randint(1, 5)

                await asyncio.sleep(delay)

                await self._engage(False)

            else:

                if not self._sequence:

                    raise errors.InvalidSession()

                await self._engage(True)

            return

        if marker is OpCode.hello:

            await self._heartbeat()

            interval = data['heartbeat_interval'] / 1000

            self._vital.inform(interval)

            self._vital.paused.set()

            self._greeting.set()

            return

    async def _identify(self):

        package, *subs = __name__.split('.', 1)

        (presence, threshold) = await self._inspect()

        data = {
            'token': self._token,
            'properties': {
                '$os': os.name,
                '$browser': package,
                '$device': package
            },
            'compress': '_query' in self._query,
            'large_threshold': threshold,
            'shard': self._info,
            'presence': presence
        }

        await self._push(OpCode.identify, data)

    async def _resume(self):

        data = {
            'token': self._token,
            'session_id': self._session_id,
            'seq': self._sequence
        }

        await self._push(OpCode.resume, data)

    async def _heartbeat(self):

        data = self._sequence

        await self._push(OpCode.heartbeat, data)

    async def _stream(self):

        while True:

            await self._saving.wait()

            if self._websocket.closed:

                await self._engage(False)

                continue

            while True:

                try:

                    (type, data, extra) = await self._websocket.__anext__()

                except (StopAsyncIteration, asyncio.CancelledError):

                    break

                self._buffer.extend(data)

                if len(data) < 4 or not data[-4:] == self._suffix:

                    continue

                try:

                    complete = self._inflator.decompress(self._buffer)

                except:

                    continue

                payload = json.loads(complete.decode('utf-8'))

                await self._pull(payload)

                self._buffer.clear()

            if self._closed:

                break

            await self._websocket.close()

    async def _connect(self):

        self._vital.paused.clear()

        while not self._closed:

            (timeout, delay) = await self._determine()

            try:

                self._websocket = await self._session.ws_connect(
                    self._url,
                    timeout = timeout
                )

            except aiohttp.ClientError:

                await asyncio.sleep(delay)

            else:

                break

        self._buffer.clear()

        self._inflator = zlib.decompressobj()

    async def _engage(self, hard):

        self._greeting.clear()

        await self._connect()

        async def observe():

            await self._greeting.wait()

            await (self._identify if hard else self._resume)()

        return self._loop.create_task(observe())

    async def _save(self):

        self._saving.clear()

        await self._websocket.close()

        complete = await self._engage(False)

        self._saving.set()

        await complete

    async def request_guild_members(self, guild_id, query = '', limit = 0):

        data = {
            'guild_id': guild_id,
            'query': query,
            'limit': limit
        }

        await self._push(OpCode.request_guild_members, data)

    async def update_voice_state(self,
                                 guild_id,
                                 channel_id,
                                 mute = False,
                                 deaf = False):

        data = {
            'guild_id': guild_id,
            'channel_id': channel_id,
            'self_mute': mute,
            'self_deaf': deaf
        }

        await self._push(OpCode.voice_state_update, data)

    async def update_status(self, status, afk, game = None, since = None):

        data = {
            'game': game,
            'status': status,
            'afk': afk,
            'since': since
        }

        await self._push(OpCode.status_update, data)

    async def start(self):

        complete = await self._engage(True)

        self._flow = self._loop.create_task(self._stream())

        await asyncio.gather(complete, loop = self._loop)

    async def close(self):

        self._closed = True

        self._vital.kill()

        self._flow.cancel()

        await self._websocket.close()

    def __repr__(self):

        shard_id, shard_count = self._info

        return f'<{self.__class__.__name__} [{shard_id}]>'
