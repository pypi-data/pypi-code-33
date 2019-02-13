import asyncio
import aiohttp
import yarl
import enum
import json
import socket
import struct

try:

    import nacl.secret as secret

except ImportError:

    secret = None

from . import vital
from . import audio


__all__ = ('Client',)


async def determine():

    return (60, 1)


USHRT_MAX = 65535


UINT_MAX = 4294967295


class OpCode(enum.IntEnum):

    identify = 0
    select_protocol = 1
    ready = 2
    heartbeat = 3
    session_description = 4
    speaking = 5
    heartbeat_ack = 6
    resume = 7
    hello = 8
    resumed = 9


class Client:

    _mode = 'xsalsa20_poly1305'

    _query = {
        'v': 3
    }

    def __init__(self,
                 session,
                 url,
                 token,
                 user_id,
                 guild_id,
                 session_id,
                 determine = determine,
                 loop = None):

        if secret is None:

            raise ModuleNotFoundError('nacl')

        if not loop:

            loop = asyncio.get_event_loop()

        self._url = yarl.URL(url).with_port(None).with_query(self._query)

        self._token = token

        self._user_id = user_id

        self._guild_id = guild_id

        self._session_id = session_id

        self._answer = asyncio.Event(loop = loop)

        self._vital = vital.Vital(self._heartbeat, self._save)

        saving = asyncio.Event(loop = loop)

        saving.set()

        self._saving = saving

        self._determine = determine

        self._socket = None

        self._websocket = None

        self._address = None

        self._ssrc = None

        self._secret = None

        self._sequence = 0

        self._timestamp = 0

        self._flow = None

        self._greeting = asyncio.Event(loop = loop)

        self._callbacks = []

        self._session = session

        self._loop = loop

        self._ready = asyncio.Event(loop = loop)

        self._closed = False

    @property
    def user_id(self):

        return self._user_id

    @property
    def guild_id(self):

        return self._guild_id

    @property
    def ready(self):

        return self._ready

    @property
    def closed(self):

        return self._closed

    def track(self, callback):

        self._callbacks.append(callback)

    __payload = ('op', 'd')

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

        (code, data) = self._break(payload)

        try:

            marker = OpCode(code)

        except ValueError:

            return

        if marker is OpCode.speaking:

            for callback in self._callbacks:

                callback(data)

            return

        if marker is OpCode.heartbeat_ack:

            self._vital.ack()

            return

        if marker is OpCode.hello:

            self._vital.ack()

            interval = data['heartbeat_interval'] * .75 / 1000

            self._vital.inform(interval)

            self._vital.paused.set()

            self._greeting.set()

            return

        if marker is OpCode.ready:

            port = data['port']

            ip = socket.gethostbyname(self._url.host)

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            sock.setblocking(False)

            self._ssrc = data['ssrc']

            packet = bytearray(70)

            struct.pack_into('>I', packet, 0, self._ssrc)

            address = (ip, port)

            self._address = address

            sock.sendto(packet, address)

            discovery = await self._loop.sock_recv(sock, 70)

            self._socket = sock

            ip_start = 4

            ip_stop = discovery.index(0, ip_start)

            ip = discovery[ip_start:ip_stop].decode('ascii')

            size = len(discovery) - 2

            port, *junk = struct.unpack_from('<H', discovery, size)

            await self._select_protocol(ip, port)

            return

        if marker is OpCode.session_description:

            secret_key = bytes(data['secret_key'])

            self._secret = secret.SecretBox(secret_key)

            await self.speaking(True)

            self._ready.set()

            return

    async def _identify(self):

        data = {
            'token': self._token,
            'user_id': self._user_id,
            'server_id': self._guild_id,
            'session_id': self._session_id,
        }

        await self._push(OpCode.identify, data)

    async def _resume(self):

        data = {
            'token': self._token,
            'server_id': self._guild_id,
            'session_id': self._session_id,
        }

        await self._push(OpCode.resume, data)

    async def _heartbeat(self):

        data = self._loop.time()

        await self._push(OpCode.heartbeat, data)

    async def _select_protocol(self, ip, port):

        data = {
            'protocol': 'udp',
            'data': {
                'address': ip,
                'port': port,
                'mode': self._mode
            }
        }

        await self._push(OpCode.select_protocol, data)

    async def _stream(self):

        severed = True

        while True:

            await self._saving.wait()

            if self._websocket.closed:

                await self._engage(severed)

            severed = not severed

            while True:

                try:

                    (type, data, extra) = await self._websocket.__anext__()

                except (StopAsyncIteration, asyncio.CancelledError):

                    break

                try:

                    payload = json.loads(data)

                except:

                    continue

                await self._pull(payload)

            if self._closed:

                break

            await self._websocket.close()

    async def _connect(self):

        self._ready.clear()

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

    async def speaking(self, start):

        data = {
            'speaking': start,
            'delay': 0,
            'ssrc': self._ssrc
        }

        await self._push(OpCode.speaking, data)

    def move(self, size):

        sequence = self._sequence + 1

        self._sequence = 0 if sequence > USHRT_MAX else sequence

        timestamp = self._timestamp + size

        self._timestamp = 0 if timestamp > UINT_MAX else timestamp

    def send(self, data):

        header = bytearray(12)

        header[0] = 0x80

        header[1] = 0x78

        struct.pack_into('>H', header, 2, self._sequence)

        struct.pack_into('>I', header, 4, self._timestamp)

        struct.pack_into('>I', header, 8, self._ssrc)

        nonce = bytearray(24)

        nonce[:12] = header

        encrypted = self._secret.encrypt(bytes(data), bytes(nonce))

        packet = header + encrypted.ciphertext

        sent = self._socket.sendto(packet, self._address)

    async def start(self):

        complete = await self._engage(True)

        self._flow = self._loop.create_task(self._stream())

        await asyncio.gather(complete, loop = self._loop)

    def audio(self, encode = True):

        size = audio.Options.samples_per_frame

        def send(data):

            self.send(data)

            self.move(size)

        client = audio.Client(send, loop = self._loop)

        async def control(data):

            await self._ready.wait()

            return data

        client.track(control)

        if encode:

            from . import opus

            rate = audio.Options.sample_rate

            channels = audio.Options.channels

            encoder = opus.Encoder(rate, channels)

            async def control(data):

                try:

                    value = encoder.encode(data, size)

                except (opus.Error, KeyboardInterrupt):

                    value = client.signal

                return value

            client.track(control)

        return client

    async def close(self):

        self._closed = True

        self._vital.kill()

        self._flow.cancel()

        await self._websocket.close()

    def __repr__(self):

        return f'<{self.__class__.__name__} [{self._url.host}]>'
