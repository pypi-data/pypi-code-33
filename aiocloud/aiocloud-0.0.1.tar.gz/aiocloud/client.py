import asyncio
import aiohttp
import yarl
import json

from . import errors
from . import storage
from . import helpers


__all__ = ('Client',)


class Client:

    _base = yarl.URL('https://api.soundcloud.com')

    def __init__(self, session, client_id):

        self._client_id = client_id

        self._session = session

    async def request(self, method, url, **kwargs):

        params = helpers.get_soft(kwargs, 'params', dict)

        helpers.fix_params(params)

        params['client_id'] = self._client_id

        response = await self._session.request(method, url, **kwargs)

        return response

    async def touch(self, method, path, **kwargs):

        url = self._base.with_path(self._base.path + path)

        response = await self.request(method, url, **kwargs)

        data = await response.text()

        if not response.status == 204:

            data = json.loads(data)

        if response.status < 400:

            return data

        raise errors.RequestError(response, data)

    _resolves = {
        'user': storage.User,
        'track': storage.Track,
        'playlist': storage.Playlist
    }

    async def resolve(self, value):

        params = {'url': value}

        data = await self.touch('GET', 'resolve', params = params)

        kind = data.pop('kind')

        structure = self._resolves[kind]

        value = structure(data)

        return value

    async def stream(self, value):

        response = await self.request('GET', value)

        length = int(response.headers['Content-Length'])

        return (response.content, length)
