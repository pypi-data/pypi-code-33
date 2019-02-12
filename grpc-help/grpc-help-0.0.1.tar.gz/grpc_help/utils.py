import concurrent
import functools
import threading
from importlib import import_module

import asyncio

try:
    import ujson as jsonlib
    has_ujson = True
except ImportError:
    import json as jsonlib
    has_ujson = False


def json_encode(value, cls=None):
    if not has_ujson:
        options = {
            "ensure_ascii": False,
            "allow_nan": False,
            "indent": None,
            "separators": (",", ":")
        }
        if cls:
            options["cls"] = cls
        return jsonlib.dumps(value, **options)

    return jsonlib.dumps(value, escape_forward_slashes=False)


def json_decode(value):
    return jsonlib.loads(value)


def import_object(obj_name):
    if obj_name is None:
        return obj_name

    elif callable(obj_name):
        return obj_name

    if not isinstance(obj_name, str):
        obj_name = obj_name.encode('utf-8')

    if obj_name.count('.') == 0:
        return __import__(obj_name, None, None)

    try:
        module_path, class_name = obj_name.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % obj_name
        raise ImportError(msg)

    obj = import_module(module_path)

    try:
        return getattr(obj, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class"' % (module_path, class_name)
        raise ImportError(msg)


class ResultIterator:
    def __init__(self, loop, async_wrapper):
        self.async_wrapper = async_wrapper
        self._loop = loop

    def __iter__(self):
        return self

    def next(self):
        async def _next():
            async for r in self.async_wrapper:
                return r

        result = self._loop.run_until_complete(_next())
        if result is None:
            raise StopIteration()
        return result

    __next__ = next


class AsyncToSync:
    def __init__(self, awaitable):
        self.awaitable = awaitable

    def __call__(self, *args, **kwargs):
        call_result = concurrent.futures.Future()
        thread = threading.current_thread()

        if not getattr(thread, "loop", None):
            new_loop = asyncio.new_event_loop()
            thread.loop = new_loop

        thread.loop.run_until_complete(self.main_wrap(args, kwargs, call_result, thread.loop))
        result = call_result.result()
        return result

    def __get__(self, parent, objtype):
        return functools.partial(self.__call__, parent)

    async def main_wrap(self, args, kwargs, call_result, loop):
        try:
            result = self.awaitable(*args, **kwargs)
            if hasattr(result, "__aiter__"):
                call_result.set_result(ResultIterator(loop, result))
            else:
                call_result.set_result(await result)
        except Exception as e:
            call_result.set_exception(e)

async_to_sync = AsyncToSync
