import logging
import datetime

from .client import Client
from .user import User
from .stream import Stream
from multidict import MultiDict
from typing import Union, List


class Helix(Client):
    BASE_URL: str = 'https://api.twitch.tv/helix/'
    COUNTER_MAX: int = 800
    TIMER_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=1)

    def __init__(self, client_id: str = None, token: str = None, loop=None):
        self.log = logging.getLogger(__name__)

        super().__init__(client_id=client_id, token=token, loop=loop)

    async def user(self, user: str = None) -> User:
        if user:
            _user = await self.users(user)
        else:
            _user = await self.users()
        if isinstance(_user, list):
            _user = _user[0]
        return _user

    async def users(self, *users: str) -> List[Union[User, str]]:
        users_clean: list = []
        users_converted: list = []
        users = list(users)

        for user in users:
            if isinstance(user, int):  # A user id can be given instead of the user login (name)
                users_clean.append(user)
            elif isinstance(user, str):  # A user login (name)
                if user.startswith('@'):  # Strip the mention symbol
                    users_clean.append(user[1:])
                else:
                    users_clean.append(user)

        if len(users_clean) > 100:
            users_cut = users_clean[100:]
            users_clean = users_clean[:100]
            users_converted.extend(await self.users(*users_cut))

        if self.cache_enabled():
            for user in users_clean:
                if self.user_cache.has(user) and not self.user_cache.expired(user):
                    users_converted.append(self.user_cache.get(user))
                    users_clean.remove(user)

        headers = {'Client-ID': self._client_id, 'Authorization': f'Bearer {self._token}'}
        params = MultiDict()

        for user in users_clean:
            if isinstance(user, int):
                params.add('id', user)
            else:
                params.add('login', user)

        response = await self.get(f'{self.BASE_URL}/users', headers=headers, params=params)

        try:
            response_json = await response.json()

            if 'data' in response_json:
                if len(response_json['data']) == 0:
                    self.log.warning(f'No data was found for {len(users_clean)} users')
                else:
                    for user_data in response_json['data']:
                        user_converted = User(self, user_data)
                        users_converted.append(user_converted)
                        self.user_cache.set(user_converted.login, user_converted)
                        self.user_cache.set(user_converted.id, user_converted)
            elif 'error' in response_json:
                self.log.error(f'An error occurred while fetching users: {response_json}')
                return users
            else:
                self.log.error('Something went wrong fetching users')
                return users
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            return users

        if len(users) == 0:
            return users_converted
        else:
            users_mixed = users
            for user in users_converted:
                if user.login in users_mixed:
                    i = users_mixed.index(user.login)
                    users_mixed[i] = user
                elif user.id in users_mixed:
                    i = users_mixed.index(user.id)
                    users_mixed[i] = user

            return users_mixed

    async def stream(self, stream) -> Stream:
        _stream = await self.streams(stream)
        if isinstance(_stream, list):
            _stream = _stream[0]
        return _stream

    async def streams(self, *streams) -> list:
        streams_clean: list = []
        streams_converted: list = []
        streams = list(streams)

        for stream in streams:
            if isinstance(stream, int):  # A stream id can be given instead of the stream login (name)
                streams_clean.append(stream)
            elif isinstance(stream, str):  # A stream login (name)
                if stream.startswith('@'):  # Strip the mention symbol
                    streams_clean.append(stream[1:])
                else:
                    streams_clean.append(stream)

        if len(streams_clean) > 100:
            streams_cut = streams_clean[100:]
            streams_clean = streams_clean[:100]
            streams_converted.extend(await self.streams(*streams_cut))

        for stream in streams_clean:
            if self.stream_cache.get(stream):
                streams_converted.append(self.stream_cache.get(stream))
                streams_clean.remove(stream)

        headers = {'Client-ID': self._client_id, 'Authorization': f'Bearer {self._token}'}
        params = MultiDict()

        for stream in streams_clean:
            if isinstance(stream, int):
                params.add('user_id', stream)
            else:
                params.add('user_login', stream)

        response = await self.get(f'{self.BASE_URL}/streams', headers=headers, params=params)

        try:
            response_json = await response.json()

            if 'data' in response_json:
                if len(response_json['data']) == 0:
                    self.log.debug(f'No data was found for {len(streams_clean)} streams')
                else:
                    for stream_data in response_json['data']:
                        stream_converted = Stream(stream_data)
                        streams_converted.append(stream_converted)
                        self.stream_cache.set(stream_converted.user_login, stream_converted)
                        self.stream_cache.set(stream_converted.user_id, stream_converted)
            elif 'error' in response_json:
                self.log.error(f'An error occurred while fetching streams: {response_json}')
            else:
                self.log.error('Something went wrong fetching streams')
        except Exception as e:
            print(e)

        streams_mixed = streams
        for stream in streams_converted:
            if stream.user_login in streams_mixed:
                i = streams_mixed.index(stream.user_login)
                streams_mixed[i] = stream
            elif stream.user_id in streams_mixed:
                i = streams_mixed.index(stream.user_id)
                streams_mixed[i] = stream

        return streams_mixed

    async def follows(self, user1: str, user2: str):
        if not isinstance(user1, User):
            user1 = await self.user(user1)
        if not isinstance(user2, User):
            user2 = await self.user(user2)

        headers = {'Client-ID': self._client_id, 'Authorization': f'Bearer {self._token}'}
        params = {'from_id': user1.id, 'to_id': user2.id}

        response = await self.get(f'{self.BASE_URL}/users/follows', headers=headers, params=params)
        response_json = await response.json()

        if 'data' in response_json and 'total' in response_json:
            if response_json['total'] > 0:
                return response_json['data'][0]['followed_at']

        return False
