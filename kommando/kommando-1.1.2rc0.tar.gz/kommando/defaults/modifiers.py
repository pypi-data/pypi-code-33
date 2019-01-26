"""
MIT License

Copyright (c) 2018 Andre Augusto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import uuid
import time
import random
import asyncio

from functools import wraps, partial 
from kommando.defaults.types import Role
from kommando.defaults.errors import ModifierError

def concurrency(level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            stats = ktx.invocation.stats
            if 'instances' not in stats:
                stats['instances'] = []
            if ktx.guild is None:
                ktx.guild = ktx.channel
            ids = [0, ktx.guild.id, ktx.channel.id,
                   ktx.author.id]
            instances = stats['instances']
            req_id = ids[level]

            if req_id not in instances:
                instances.append(req_id)
                try:
                    return await f(ktx, *args, **kwargs)
                except Exception as err:
                    raise err
                finally:
                    del instances[instances.index(req_id)]
            raise ModifierError(0, level=level)
        return decorated
    return decorator

def cooldown(seconds=5, level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            stats = ktx.invocation.stats
            if 'cooldowns' not in stats:
                stats['cooldowns'] = {}
            c = stats['cooldowns']
            if ktx.guild is None:
                ktx.guild = ktx.channel
            ids = [0, ktx.guild.id, ktx.channel.id,
                   ktx.author.id]
            req_id = ids[level]

            if req_id in c:
                wait = seconds - (time.time() - c[req_id])
                cold = wait <= 0
            else:
                wait = 0
                cold = True

            if cold:
                c[req_id] = time.time()
                return await f(ktx, *args, **kwargs)
            else:
                raise ModifierError(1, seconds=seconds, 
                                    level=level, wait=wait)
        return decorated
    return decorator

def use_limit(uses, seconds=60, level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            stats = ktx.invocation.stats
            if 'use_limit' not in stats:
                stats['use_limit'] = {}
            c = stats['use_limit']
            if ktx.guild is None:
                ktx.guild = ktx.channel
            ids = [0, ktx.guild.id, ktx.channel.id,
                   ktx.author.id]
            req_id = ids[level]

            if req_id in c:
                u_uses, at_time = c[req_id]
                wait = seconds - (time.time() - at_time)
                cold = wait <= 0
            else:
                u_uses, at_time = (0, time.time())
                wait = 0
                cold = True

            if u_uses < uses:
                c[req_id] = (u_uses + 1, at_time)
            elif cold:
                c[req_id] = (0, time.time())
            else:
                raise ModifierError(2, uses=uses, 
                                    seconds=seconds, level=level, 
                                    wait=wait)
            return await f(ktx, *args, **kwargs)
        return decorated
    return decorator

def need_perms(*perms, mode='all', target=None):
    if mode not in ['all', 'any']:
        raise ValueError('Unknown mode')
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            p = []
            r = ktx.author.roles if target is None else target.roles
            for role in r:
                p.extend(role.permissions)
            p = set([x[0] for x in p if x[1]])
            if eval(mode)([x in p for x in perms]):
                return await f(ktx, *args, **kwargs)
            else:
                raise ModifierError(3, perms=perms, 
                                    mode=mode, target=target)
        return decorated
    return decorator

def need_roles(*roles, mode='all', target=None):
    if mode not in ['all', 'any']:
        raise ValueError('Unknown mode')
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            r = ktx.author.roles if target is None else target.roles
            if eval(mode)([Role(ktx, x) in r for x in roles]):
                return await f(ktx, *args, **kwargs)
            raise ModifierError(4, roles=roles, 
                                mode=mode, target=target)
        return decorated
    return decorator

def _evaluator(source, num):
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            if eval(source):
                return await f(ktx, *args, **kwargs)
            else:
                raise ModifierError(num)
        return decorated
    return decorator

owner_only = _evaluator("ktx.author.id in ktx.bot.owners", 5)
dm_only = _evaluator("ktx.guild is None", 6)
guild_only = _evaluator("ktx.guild is not None", 7)
nsfw_only = _evaluator('ktx.message.channel.is_nsfw()', 8)
safe_only = _evaluator('not ktx.message.channel.is_nsfw()', 9)

def checker(function, err=None):
    def decorator(f):
        @wraps(f)
        async def decorated(ktx, *args, **kwargs):
            if await asyncio.coroutine(function)(ktx):
                return await f(ktx, *args, **kwargs)
            else:
                if err is not None:
                    raise err
        return decorated
    return decorator
