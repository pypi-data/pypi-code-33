import logging
import datetime

from twitchbot.api.client import Client
from twitchbot.api.user import User
from twitchbot.api.game import Game
from twitchbot.api.stream import Stream
from multidict import MultiDict
from typing import Union, List


class Kraken(Client):
    BASE_URL: str = 'https://api.twitch.tv/kraken'
    COUNTER_MAX: int = 800
    TIMER_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=1)

    def __init__(self, client_id: str = None, token: str = None, loop=None):
        self.log = logging.getLogger(__name__)

        super().__init__(client_id=client_id, token=token, loop=loop)

    async def update_channel(self, channel_id: int, status=None, game=None):
        headers = {'Client-ID': self._client_id, 'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': f'OAuth {self._token}'}
        params = {}
        payload = {}

        if status:
            payload['channel[status]'] = status
        if game:
            payload['channel[game]'] = game

        response = await self.put(self.BASE_URL + f'/channels/{channel_id}', headers=headers, params=params,
                                  data=payload)

        if response.status is not 200:
            if not await self._unauthorized():
                return False
            else:
                return await self.update_channel(channel_id, status, game)

        return True
