import logging
import datetime

from multidict import MultiDict
from typing import Union, List
from twitchbot.api.client import Client
from twitchbot.api.user import User
from twitchbot.api.game import Game
from twitchbot.api.stream import Stream


class Helix(Client):
    BASE_URL: str = 'https://api.twitch.tv/helix'
    COUNTER_MAX: int = 800
    TIMER_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=1)

    def __init__(self, client_id: str = None, token: str = None, loop=None):
        self.log = logging.getLogger(__name__)

        super().__init__(client_id=client_id, token=token, loop=loop)

    async def user(self, user: Union[str, int] = None) -> User:
        if user:
            _user = await self.users(user)
        else:
            _user = await self.users()
        if isinstance(_user, list):
            _user = _user[0]
        return _user

    async def users(self, *users: Union[str, int]) -> List[Union[User, str, int]]:
        users_clean: list = []
        users_converted: list = []
        users = list(users)

        for user in users:
            if isinstance(user, int):  # A user id can be given instead of the user login (name)
                users_clean.append(user)
            elif isinstance(user, str):  # A user login (name)
                if user.startswith('@'):  # Strip the mention symbol
                    users_clean.append(user[1:].lower())
                else:
                    users_clean.append(user.lower())

        if len(users_clean) > 100:
            users_cut = users_clean[100:]
            users_clean = users_clean[:100]
            users_converted.extend(await self.users(*users_cut))

        if self.cache_enabled():
            for user in users_clean:
                if self.user_cache.has(user) and not self.user_cache.expired(user):
                    users_converted.append(self.user_cache.get(user))
                    users_clean.remove(user)

        if len(users_clean) > 0 or (len(users_clean) == 0 and len(users) == 0):
            headers = {'Client-ID': self._client_id, 'Authorization': f'Bearer {self._token}'}
            params = MultiDict()

            for user in users_clean:
                if isinstance(user, int):
                    params.add('id', str(user))
                else:
                    params.add('login', user)

            response = await self.get(f'{self.BASE_URL}/users', headers=headers, params=params)

            if response.status is not 200:
                if response.status is 401:
                    if not await self._unauthorized():
                        return users
                    else:
                        return await self.users(*users)
                else:
                    return users

            try:
                response_json = await response.json()

                if 'data' in response_json:
                    if len(response_json['data']) == 0:
                        self.log.warning(f'No data was found for {len(users_clean)} user(s)')
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
                streams_clean.append(stream.lower())

        if len(streams_clean) > 100:
            streams_cut = streams_clean[100:]
            streams_clean = streams_clean[:100]
            streams_converted.extend(await self.streams(*streams_cut))

        for stream in streams_clean:
            if self.stream_cache.get(stream):
                streams_converted.append(self.stream_cache.get(stream))
                streams_clean.remove(stream)

        if len(streams_clean) > 0:
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
                        self.log.debug(f'No data was found for {len(streams_clean)} stream(s)')
                    else:
                        for stream_data in response_json['data']:
                            stream_converted = Stream(self, stream_data)
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

    async def game(self, game: Union[str, int]) -> Game:
        _game = await self.games(game)
        if isinstance(_game, list):
            _game = _game[0]
        return _game

    async def games(self, *games: Union[str, int]) -> List[Union[Game, str]]:
        games_clean: List[Union[str, int]] = []
        games_converted: List[Game] = []
        games: List[Union[str, int]] = list(games)

        for game in games:
            if isinstance(game, int):  # A game id can be given instead of the game name
                games_clean.append(game)
            elif isinstance(game, str):  # A game name
                    games_clean.append(game.lower())

        if len(games_clean) > 100:
            games_cut = games_clean[100:]
            games_clean = games_clean[:100]
            games_converted.extend(await self.games(*games_cut))

        if self.cache_enabled():
            for game in games_clean:
                if self.game_cache.has(game) and not self.game_cache.expired(game):
                    games_converted.append(self.game_cache.get(game))
                    games_clean.remove(game)

        if len(games_clean) > 0:
            headers = {'Client-ID': self._client_id, 'Authorization': f'Bearer {self._token}'}
            params = MultiDict()

            for game in games_clean:
                if isinstance(game, int):
                    params.add('id', game)
                else:
                    params.add('name', game)

            response = await self.get(f'{self.BASE_URL}/games', headers=headers, params=params)

            try:
                response_json = await response.json()

                if 'data' in response_json:
                    if len(response_json['data']) == 0:
                        self.log.warning(f'No data was found for {len(games_clean)} game(s)')
                    else:
                        for game_data in response_json['data']:
                            game_converted = Game(self, game_data)
                            games_converted.append(game_converted)
                            self.game_cache.set(game_converted.name, game_converted)
                            self.game_cache.set(game_converted.id, game_converted)
                elif 'error' in response_json:
                    self.log.error(f'An error occurred while fetching games: {response_json}')
                    return games
                else:
                    self.log.error('Something went wrong fetching games')
                    return games
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
                return games

        if len(games) == 0:
            return games_converted
        else:
            games_mixed: List[Union[Game, str, int]] = games
            for game in games_converted:
                if game.name in games_mixed:
                    i = games_mixed.index(game.name)
                    games_mixed[i] = game
                elif game.id in games_mixed:
                    i = games_mixed.index(game.id)
                    games_mixed[i] = game

            return games_mixed
