import json
import sys
from collections.abc import Iterable, Mapping

import click
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import JsonLexer

from ._types import ShopifyObjectBase


def isatty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


def print_object(obj, stream=None, fmt=None):
    if stream is None:
        stream = sys.stdout
    _tty = isatty(stream)

    if fmt is None:
        if _tty:
            return print_object_human(obj, stream)
        return print_object_json(obj, stream)

    if fmt == 'json':
        if _tty:
            return print_object_json_pretty(obj, stream)
        return print_object_json(obj, stream)

    if fmt == 'human':
        return print_object_human(obj, stream)

    raise ValueError('Invalid output format: {}'.format(fmt))


def print_object_json(obj, stream):
    json.dump(obj, stream, default=json_default)


def print_object_json_pretty(obj, stream):
    serialized = json.dumps(obj, default=json_default, indent=4)
    highlighted = highlight(
        serialized,
        JsonLexer(),
        Terminal256Formatter(style='monokai'))
    click.echo(highlighted, file=stream)


def json_default(value):

    if isinstance(value, ShopifyObjectBase):
        return value.data

    if isinstance(value, Iterable):
        # Generators etc
        return list(value)

    raise TypeError('Object of type {} is not JSON serializable'
                    .format(type(value)))


def print_object_human(obj, stream):
    # FIXME: actually print objects in a more human-friendly way
    return print_object_json_pretty(obj, stream)
