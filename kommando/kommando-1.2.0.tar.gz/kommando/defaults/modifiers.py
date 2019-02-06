"""
MIT License

Copyright (c) 2019 Andre Augusto

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
import types
import random
import asyncio

from types import MethodType
from functools import wraps, partial 
from kommando.defaults.types import Role
from kommando.defaults.errors import ModifierError

def _get_unique(name, l):
    n = 0
    result = name
    while True:
        if result not in l:
            return result
        result = f'{name}_{n}'
        n += 1

def _call_checker(f):
    def decorator(f2):
        @wraps(f2)
        async def __call__(self, ktx, *args, **kwargs):
            modify = kwargs['modify'] \
                        if 'modify' in kwargs \
                        else True
            if not modify or await asyncio.coroutine(f)(ktx):
                return await asyncio.coroutine(f2)(ktx, *args, **kwargs)
        return __call__
    return decorator

def _set_call(inv, f):
    inv.__class__ = type(f'Modified{type(inv).__name__}', (inv.__class__,), 
                         {**inv.__dict__, '__call__': f})

def checker(f):
    def modifier(inv):
        _set_call(inv, _call_checker(f)(inv.__call__))
        return inv
    return modifier

def concurrency(level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def modifier(inv):
        if 'instances' not in inv.stats:
            instances = inv.stats['instances'] = []
        def decorator(f):
            @wraps(f)
            async def __call__(self, ktx, *args, **kwargs):
                if ktx.guild is None:
                    ktx.guild = ktx.channel
                ids = [0, ktx.guild.id, ktx.channel.id,
                       ktx.author.id]
                req_id = ids[level]
                
                modify = kwargs['modify'] \
                         if 'modify' in kwargs \
                         else True

                if not modify or req_id not in instances:
                    instances.append(req_id)
                    try:
                        c = asyncio.coroutine(f)
                        return await c(ktx, *args, **kwargs)
                    except Exception as err:
                        raise err
                    finally:
                        del instances[instances.index(req_id)]
                raise ModifierError(0, level=level)
            return __call__
        _set_call(inv, decorator(inv.__call__))
        return inv
    return modifier

def cooldown(seconds=5, level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def modifier(inv):
        name = _get_unique('cooldown', inv.stats)
        d = inv.stats[name] = {}
        async def check(ktx, d=d):
            if ktx.guild is None:
                ktx.guild = ktx.channel
            ids = [0, ktx.guild.id, ktx.channel.id,
                   ktx.author.id]
            req_id = ids[level]

            if req_id in d:
                wait = seconds - (time.time() - d[req_id])
                cold = wait <= 0
            else:
                wait = 0
                cold = True

            if not cold:
                raise ModifierError(1, seconds=seconds, 
                                    level=level, wait=wait)
            d[req_id] = time.time()
            return True
        return checker(check)(inv)
    return modifier

def use_limit(uses, seconds=60, level=3):
    if level > 3:
        raise ValueError(f"Level {level} don't exist")
    def modifier(inv):
        name = _get_unique('use_limit', inv.stats)
        d = inv.stats[name] = {}
        async def check(ktx, d=d):
            if ktx.guild is None:
                ktx.guild = ktx.channel
            ids = [0, ktx.guild.id, ktx.channel.id,
                    ktx.author.id]
            req_id = ids[level]

            if req_id in d:
                u_uses, at_time = d[req_id]
                wait = seconds - (time.time() - at_time)
                cold = wait <= 0
            else:
                u_uses, at_time = (0, time.time())
                wait = 0
                cold = True

            if u_uses < uses:
                d[req_id] = (u_uses + 1, at_time)
            elif cold:
                d[req_id] = (0, time.time())
            else:
                raise ModifierError(2, uses=uses, 
                                    seconds=seconds, level=level, 
                                    wait=wait)
            return True
        return checker(check)(inv)
    return modifier

def need_perms(*perms, mode='all', target=None):
    if mode not in ['all', 'any']:
        raise ValueError('Unknown mode')
    async def check(ktx):
        p = []
        r = ktx.author.roles if target is None else target.roles
        for role in r:
            p.extend(role.permissions)
        p = set([x[0] for x in p if x[1]])
        if eval(mode)([x in p for x in perms]):
            return True
        else:
            raise ModifierError(3, perms=perms, 
                                mode=mode, target=target)
    return checker(check)

def need_roles(*roles, mode='all', target=None):
    async def check(ktx):
        r = ktx.author.roles if target is None else target.roles
        if eval(mode)([Role(ktx, x) in r for x in roles]):
            return True
        raise ModifierError(4, roles=roles, 
                            mode=mode, target=target)
    return checker(check)

def _evaluator(source, num):
    async def check(ktx):
        if eval(source):
            return True
        else:
            raise ModifierError(num)
    return checker(check)

owner_only = _evaluator("ktx.author.id in ktx.bot.owners", 5)
dm_only = _evaluator("ktx.guild is None", 6)
guild_only = _evaluator("ktx.guild is not None", 7)
nsfw_only = _evaluator('ktx.message.channel.is_nsfw()', 8)
safe_only = _evaluator('not ktx.message.channel.is_nsfw()', 9)
