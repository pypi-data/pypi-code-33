# -*- coding: utf-8 -*-

from enum import Enum
from ..registry import ROUTES_PENDING


class Route:
    handler = None
    name = None
    schema = None

    def __init__(self, path, method):
        self.path = path
        self.method = method

    def set_handler(self, handler, name):
        self.handler = handler
        self.name = name


class Method(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'


def route(*args, **kwargs):
    path = kwargs.pop('path', args[0])
    method = kwargs.pop('method', args[1])
    injectors = kwargs.pop('inject', [])

    if isinstance(method, str):
        method = Method(method.upper()).value

    _route = Route(path, method)

    def wrapper(fn):
        #async def handler(self, request, *wrapped_args, **wrapped_kwargs):
        #    return await fn(self, request, *wrapped_args, **wrapped_kwargs)

        _route.set_handler(fn, fn.__name__)

        # Add pending route for later registration
        hid = id(_route.handler)
        ROUTES_PENDING[hid] = _route

        # return handler
        return fn

    return wrapper
