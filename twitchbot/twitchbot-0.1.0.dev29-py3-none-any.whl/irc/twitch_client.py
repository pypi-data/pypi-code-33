import logging
import aiohttp
import datetime

from .client import Client


class TwitchClient(Client):
    def __init__(self, nickname: str = None, token: str = None, channel: str = None, loop=None):
        self.log = logging.getLogger(__name__)

        super().__init__(nickname=nickname, token=token, channel=channel, loop=loop)

        self._is_mod = False
        self._last_mod_check = None
        self._send_counter_max = 20
        self._send_counter_max_mod = 100
        self._send_session_td = datetime.timedelta(seconds=30)
        self.session = aiohttp.ClientSession(loop=self._event_loop)

    async def connect(self, host: str = 'irc.chat.twitch.tv', port: int = 6667) -> None:
        return await super().connect(host, port)

    async def cap(self, capability: str) -> str:
        capability = 'twitch.tv/' + capability
        return await super().cap(capability)

    async def send_pmsg(self, message):
        await self.send(f'PRIVMSG #{self._channel} :{message}')

    async def send_session_check(self):
        if not self._send_session_dt or (self._send_session_dt + self._send_session_td < datetime.datetime.now()):
            await self.send_session_reset()

        if not self._last_mod_check or self._last_mod_check + datetime.timedelta(minutes=5) < datetime.datetime.now():
            viewers = await self.viewers()
            self._is_mod = self._nickname in viewers['moderators']
            self._last_mod_check = datetime.datetime.now()
            self.log.debug(f'IRC moderator status set to {self._is_mod}')

        if self._is_mod:
            return self._send_counter < self._send_counter_max_mod
        return self._send_counter < self._send_counter_max

    async def viewers(self):
        response = await self.session.get(
            f'http://tmi.twitch.tv/group/user/{self._channel}/chatters')

        response_json = await response.json()
        viewers = {'all': []}
        if 'chatters' in response_json:
            for rank in response_json['chatters']:
                if rank not in viewers:
                    viewers[rank] = []

                if len(response_json['chatters'][rank]) > 0:
                    viewers['all'].extend([x.lower() for x in response_json['chatters'][rank] if x not in viewers['all']])
                    viewers[rank].extend([x.lower() for x in response_json['chatters'][rank] if x not in viewers[rank]])

        return viewers

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()
