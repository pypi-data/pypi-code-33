import asyncio
import aiohttp
import yarl
import enum
import json
import socket
import struct

try:

    import nacl

except ImportError:

    nacl = None

from . import errors
from . import vital


__all__ = ('Client',)


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
    client_disconnect = 13


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
                 loop = None):

        if nacl is None:

            raise ModuleNotFoundError('nacl')

        if not loop:

            loop = asyncio.get_event_loop()

        self._url = yarl.URL(url)

        self._token = token

        saving = asyncio.Event(loop = loop)

        saving.set()

        self._saving = saving

        self._vital = vital.Vital(self._heartbeat, self._save)

        self._socket = None

        self._websocket = None

        self._address = None

        self._ssrc = None

        self._secret = None

        self._sequence = 0

        self._timestamp = 0

        self._flow = None

        self._greeting = asyncio.Event(loop = loop)

        self._session = session

        self._loop = loop

    @property
    def user_id(self):

        return self._user_id

    @property
    def guild_id(self):

        return self._guild_id

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

        await self._saving.wait()

        payload = self._build(*values)

        await self._websocket.send_json(payload)

    async def _pull(self, payload):

        (code, data) = self._break(payload)

        try:

            marker = OpCode(code)

        except ValueError:

            return

        if marker is OpCode.hello:

            interval = data['heartbeat_interval'] * .75 / 1000

            self._vital.inform(interval)

            self._vital.paused.set()

            self._greeting.set()

            return

        if market is OpCode.ready:

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

        if code is enums.OpCode.session_description:

            secret_key = bytes(data['secret_key'])

            self._secret = nacl.secret.SecretBox(secret_key)

            await self.speaking(True)

            return

        if marker is OpCode.heartbeat_ack:

            self._vital.ack()

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

        await self._push(enums.OpCode.select_protocol, data)

    async def _stream(self):

        while not self._session.closed:

            await self._saving.wait()

            if self._websocket.closed:

                await self._resurrect(severed)

                severed = True

                continue

            severed = False

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

        await self.close()

    async def _connect(self):

        self._vital.paused.clear()

        while not self._session.closed:

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

    async def _resurrect(self, hard):

        self._greeting.clear()

        await self._connect()

        async def engage():

            await self._greeting.wait()

            await (self._identify if hard else self._resume)()

        task = self._loop.create_task(engage())

        return task

    async def _save(self):

        self._saving.clear()

        await self._websocket.close()

        engaging = await self._resurrect(False)

        self._saving.set()

        await engaging

    async def speaking(self, start):

        data = {
            'speaking': start,
            'delay': 0,
            'ssrc': self._ssrc
        }

        await self._push(enums.OpCode.speaking, data)

    def move(self, samples):

        sequence = self._sequence + 1

        self._sequence = 0 if sequence > USHRT_MAX else sequence

        timestamp = self._timestamp + samples

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

        await self._connect()

        self._flow = self._loop.create_task(self._stream())

        await self._greeting.wait()

        await self._identify()

    async def close(self):

        self._vital.kill()

        self._flow.cancel()

        await self._websocket.close()

    def __repr__(self):

        return f'<{self.__class__.__name__} [{self._url}]>'
