# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from operator import methodcaller

from rpy.functions.api import asyncio
from rpy.functions.decorators import to_tuple
from rpy.functions.functional import first, iterate


async def _id(id, task):
    return id, await task

async def wait_all(*args):
    done = tuple(_id(i, t) for i, t in enumerate(iterate(*args)))
    if done:
        futures, p = await asyncio.wait(done)
        futures = dict(map(methodcaller('result'), futures))
        return tuple(futures[i] for i in range(len(done)))
    return done

def run_all(*args, **opts):
    done = tuple(iterate(*args))
    if done and len(done) > 1:
        return asyncio.ensure_future(asyncio.wait(done), **opts)
    elif done:
        return asyncio.ensure_future(first(done), **opts)
    return done


def get_event_loop(loop=None):
    try:
        return loop or asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop




@to_tuple
def syncronous_wait_all(*args, loop=None):
    yield from (loop or get_event_loop()).run_until_complete(wait_all(*args))
