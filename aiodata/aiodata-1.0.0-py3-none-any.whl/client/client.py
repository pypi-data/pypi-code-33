import asyncio
import aiohttp
import yarl
import collections
import functools
import copy
import aiocogs

from . import errors
from . import state
from . import cache
from . import helpers


__all__ = ('Client',)


class Base:

    __slots__ = ('_session', '_url', '_authorize')

    _errors = {
        401: errors.AuthorizationError,
        400: errors.BadRequestError
    }

    _valid = (*_errors.keys(), 200)

    def __init__(self, session, url, authorize):

        self._session = session

        self._url = yarl.URL(url)

        self._authorize = authorize

    async def request(self, method, path, **kwargs):

        self._authorize(kwargs)

        clean = self._url.path.rstrip('/')

        url = self._url.with_path(clean + path)

        response = await self._session.request(method, url, **kwargs)

        data = await response.json() if response.status in self._valid else None

        if response.status < 400:

            return data

        try:

            error = self._errors[response.status]

        except KeyError:

            error = errors.RequestError

        if data:

            code, *info = data

        else:

            code, info = (None,) * 2

        raise error(response, code, info)


class Client(Base):

    __slots__ = ('_cache', '_tracks', '_state', '_ready', '_closed', '_loop')

    def __init__(self, *args, loop = None):

        super().__init__(*args)

        if not loop:

            loop = asyncio.get_event_loop()

        self._cache = None

        self._tracks = collections.defaultdict(
            functools.partial(
                collections.defaultdict,
                list
            )
        )

        self._state = None

        self._ready = asyncio.Event(loop = loop)

        self._closed = False

        self._loop = loop

    @property
    def cache(self):

        return self._cache

    async def request(self, method, name, *data):

        path = '/' + name

        data = await super().request(method, path, json = data)

        return map(cache.Entry, data)

    def get(self, name, *keys):

        return self.request('GET', name, keys)

    def create(self, name, *keys, **data):

        return self.request('POST', name, keys, data)

    def update(self, name, *keys, **data):

        return self.request('PATCH', name, keys, data)

    def delete(self, name, *keys):

        return self.request('PATCH', keys)

    _methods = {
        'create': 'POST',
        'update': 'PATCH',
        'delete': 'DELETE'
    }

    def track(self, action, name):

        method = self._methods[action]

        def wrapper(function):

            self._tracks[method][name].append(function)

            return function

        return wrapper

    def _ePOST(self, name, data):

        entries = self._cache[name]

        entry = entries.create(data)

        return entry

    def _ePATCH(self, name, data):

        entries = self._cache[name]

        query = entries.query(data)

        entry = entries.get(*query)

        fake = copy.copy(entry)

        helpers.update_value(entry, data)

        return (fake, entry)

    def _eDELETE(self, name, data):

        entries = self._cache[name]

        query = entries.query(data)

        entry = entries.destroy(*query)

        return entry

    async def handle(self, method, name, data, prefix = '_e'):

        await self._ready.wait()

        handle = getattr(self, prefix + method)

        entries = tuple(handle(name, value) for value in data)

        try:

            callbacks = self._tracks[method][name]

        except KeyError:

            return

        coroutines = (callback(entries) for callback in callbacks)

        await asyncio.gather(*coroutines, loop = self._loop)

    async def _build(self, names, stores):

        coroutines = map(self.get, names)

        tasks = tuple(map(self._loop.create_task, coroutines))

        async for task in aiocogs.ready(*tasks, loop = self._loop):

            values = task.result()

            index = tasks.index(task)

            store = stores[index]

            for value in values:

                data = value.__dict__

                store.create(data)

        self._ready.set()

    def _callback(self, data, prefix = '_e'):

        if self._cache:

            (method, name, payload) = data

            coroutine = self.handle(method, name, payload)

        else:

            names, keys = zip(*data)

            stores = [cache.Entries(cache.Entry, key) for key in keys]

            entry = dict(zip(names, stores))

            self._cache = cache.Entry(entry)

            coroutine = self._build(names, stores)

        self._loop.create_task(coroutine)

    async def connect(self, path):

        params, headers = {}, {}

        options = {'params': params, 'headers': headers}

        self._authorize(options)

        path = self._url.path.rstrip('/') + path

        url = self._url.with_path(path).with_query(params)

        websocket = await self._session.ws_connect(url, headers = headers)

        return state.State(websocket, self._callback, loop = self._loop)

    async def manage(self, execute, retry):

        while not self._closed:

            while not self._closed:

                try:

                    state = await execute()

                except aiohttp.ClientConnectionError:

                    await asyncio.sleep(retry)

                else:

                    break

            else:

                break

            self._state = state

            await self._state.start()

    async def start(self, path, retry = 0.5):

        connect = functools.partial(self.connect, path)

        coroutine = self.manage(connect, retry)

        self._loop.create_task(coroutine)

        await self._ready.wait()

    async def close(self):

        self._closed = True

        await self._state.close()
