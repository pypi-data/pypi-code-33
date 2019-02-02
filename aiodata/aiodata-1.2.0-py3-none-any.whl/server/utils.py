import asyncio
import aiohttp.web
import functools

from . import access
from . import seed
from . import handle


__all__ = ()


def authorization(error, key, value, store):

    try:

        provide = store[key]

    except KeyError:

        raise error('missing')

    if provide == value:

        return

    raise error('invalid')


def fail(cls, *data):

    response = aiohttp.web.json_response(data)

    return cls(body = response.body, content_type = response.content_type)


authorization_header = 'Authorization'


authorization_error = aiohttp.web.HTTPUnauthorized


authorization_fail = functools.partial(fail, authorization_error)


authorization_parts = (authorization_fail, authorization_header)


specific_authorize = functools.partial(authorization, *authorization_parts)


def specific_authorization(spot, value, request):

    store = getattr(request, spot)

    specific_authorize(value, store)


authorization_spot = 'headers'


authorize = functools.partial(specific_authorization, authorization_spot)


authorizer = lambda value: functools.partial(authorize, value)


handle_error = aiohttp.web.HTTPBadRequest


handle_fail = functools.partial(fail, authorization_error)


ignore = ('GET',)


methods = (*ignore, 'POST', 'PATCH', 'DELETE')


def listen(alert, handle):

    async def wrapper(request):

        data = await handle(request)

        await alert(data)

        return aiohttp.web.json_response(data)

    return wrapper


silent = asyncio.coroutine(lambda *args: None)


def setup(client, objects, model, authorize, fail, parse = tuple):

    _access = access.Access(objects, model)

    client.add_info(_access.name, _access.primary)

    _seed = seed.Seed(_access, parse)

    _handle = handle.Handle(_seed, authorize, fail)

    sub_handlers = (_handle.get, _handle.create, _handle.update, _handle.delete)

    controller = '/' + _access.name

    def vocal(*args):

        async def wrapper(data):

            await client.dispatch(*args, data)

        return wrapper

    for (method, sub_handler) in zip(methods, sub_handlers):

        dispatch = silent if method in ignore else vocal(method, _access.name)

        handler = listen(dispatch, sub_handler)

        yield (method, controller, handler)
