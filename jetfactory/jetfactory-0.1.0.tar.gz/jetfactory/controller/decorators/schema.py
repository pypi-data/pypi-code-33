# -*- coding: utf-8 -*-

import ujson

from functools import wraps
from sanic.response import HTTPResponse
from ..registry import REQUEST_SCHEMAS


def schema(_schema, load=True, dump=True, status=200):
    if not hasattr(_schema, 'Meta'):
        meta = type('Meta', (type,), {})
        _schema.Meta = meta

    _schema.Meta.render_module = ujson
    sch = _schema()

    attrs_known = [
        ('query', 'args'),
        ('path', 'match_info'),
        ('body', 'json'),
        ('response', 'response')
    ]
    req_fields = []

    for attr, field in sch.declared_fields.items():
        known = dict(attrs_known)

        if attr not in known.keys():
            raise Exception(f'{_schema}.{attr} is unknown. Must be one of: {known.keys()}')

        req_fields.append((attr, known[attr]))

    def wrapper(fn):
        @wraps(fn)
        async def handler(*args, **kwargs):
            args_new = list(args)
            request = args_new.pop(1)
            input_data = {}

            for attr_name, req_name in req_fields:
                # Don't even attempt to load response as input
                if 'response' in [attr_name, req_name]:
                    continue

                input_data[attr_name] = getattr(request, req_name)

            if load:
                # Validate and transform
                extra_args = sch.load(input_data)

                # Path components are already injected by Sanic.
                extra_args.pop('path', None)

                kwargs.update(extra_args)

            rv = await fn(*args_new, **kwargs)
            if not dump or isinstance(rv, HTTPResponse):
                return rv

            return HTTPResponse(
                body=sch.dumps({'response': rv}, indent=4),
                status=status,
                content_type='application/json'
            )

        hid = id(handler)
        REQUEST_SCHEMAS[hid] = sch

        return handler

    return wrapper
