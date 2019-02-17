import logging
import asyncio
import datetime

from .message import Message


class Client:
    def __init__(self, nickname: str = None, token: str = None, channel: str = None, loop=None):
        if not hasattr(self, 'log'):
            self.log = logging.getLogger(__name__)
        self.log.debug('Initialization complete')

        self._channel = channel
        self._nickname = nickname
        self._token = token

        self._capabilities = {}

        self._event_loop = loop if loop is not None else asyncio.get_event_loop()

        self._reader = None
        self._writer = None
        self._send_buffer = asyncio.Queue(loop=self._event_loop)
        self._send_counter = 0
        self._send_counter_max = 30
        self._send_session_dt = None
        self._send_session_td = datetime.timedelta(seconds=30)

        asyncio.ensure_future(self._sender(), loop=self._event_loop)

    async def connect(self, host: str, port: int = 6667) -> None:
        self._reader, self._writer = await asyncio.open_connection(host, port, loop=self._event_loop)

        self.log.info(f'Connected to {host}:{port}')

    async def is_connected(self):
        return not self._reader.at_eof()

    async def login(self, nickname: str = None, token: str = None):
        if not nickname:
            nickname = self._nickname

        if not token:
            token = self._token

        await self.send(f'PASS oauth:{token}')
        await self.send(f'NICK {nickname.lower()}')

        while True:
            response = await self.receive()

            if response.status == 376:
                self.log.info(f'Logged in using NICK: {nickname}')
                break
            elif 'Login authentication failed' in response.content:
                raise ConnectionError('Authentication failed')

    async def cap(self, capability: str):
        await self.send(f'CAP REQ :{capability.lower()}')

        while True:
            response = await self.receive()

            if response.capability:
                self._capabilities[response.capability.lower()] = True

                if response.capability.lower() == capability.lower():
                    break

    async def join(self, channel: str = None):
        if not channel:
            channel = self._channel

        await self.send(f'JOIN #{channel.lower()}')

        while True:
            response = await self.receive()

            if response.status == 366:
                self.log.info(f'Joined channel {channel}')
                break

    async def send(self, message):
        await self._send_buffer.put(message)

    async def _sender(self):
        while True:
            await asyncio.sleep(0)
            if self._writer and await self.send_session_check():
                msg = await self._send_buffer.get()
                self._writer.write(bytes(msg + "\r\n", 'utf-8'))
                self.log.debug(' > %s' % msg)
                self._send_counter += 1
                self._send_buffer.task_done()

    async def send_session_check(self):
        if not self._send_session_dt or (self._send_session_dt + self._send_session_td < datetime.datetime.now()):
            await self.send_session_reset()
        return self._send_counter < self._send_counter_max

    async def send_session_reset(self):
        self._send_session_dt = datetime.datetime.now()
        self._send_counter = 0

    async def receive(self):
        if not await self.is_connected():
            raise EOFError('Connection was broken.')

        try:
            response = await asyncio.wait_for(self._reader.readline(), timeout=300)
            response = response.decode('utf-8').rstrip()
            response = Message(response)

            if response.content:
                self.log.debug(f' < {response.author + ":" if response.author else ""}{response.content}')
            elif response.tags:
                self.log.debug(f' < {response.author + ":" if response.author else ""}{", ".join("{}: {}".format(key, value) for key, value in response.tags.items())}')
            else:
                self.log.debug(f' < {response.author + ":" if response.author else ""}')

            if response.content == 'PING :tmi.twitch.tv':
                await self.send('PONG :tmi.twitch.tv')
                return await self.receive()  # Try receiving another message.
            else:
                return response
        except TimeoutError:
            raise TimeoutError('Connection timed out.')
        except asyncio.TimeoutError:
            # The maximum wait_for has been reached. This means Twitch is not sending pings anymore.
            raise TimeoutError('Took too long to read line.')

    async def close(self):
        if self._writer:
            self._writer.close()
