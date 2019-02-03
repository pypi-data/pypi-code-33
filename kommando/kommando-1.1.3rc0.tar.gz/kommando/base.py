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

import os
import sys
import copy
import time
import asyncio
import difflib
import discord
import inspect
import logging
import importlib
import traceback
import collections

from copy import deepcopy
from functools import wraps, lru_cache, partial

from kommando.defaults.errors import ParsingError

# Context and helper class

class UnfittedContext(Exception):
    MSG = 'No invocation fit this context'
    def __init__(self):
        super().__init__(self.MSG)

class Kontext:
    def __init__(self, bot, message):
        self.bot = bot
        self._message = copy.copy(message)

        self.message = message
        self.author = message.author
        self.channel = message.channel
        self.guild = message.guild

        self.extension = None
        self.section = None
        self.invocation = None
        self.log = bot.log

    async def load(self, path, invocation):
        """
        Loads the path and the invocation
        This function exists for
        possible extensions
        """
        self.path = path
        self.invocation = invocation
        self.extension = invocation.extension
        self.section = invocation.section

    async def fit(self, invocations):    
        """
        Iterates over all invocations to find 
        whose fits the ctx, using __check__
        __check__ needs to return a Class or a false value

        Returns a path and a invocation
        """
        for k, v in self.bot.walk_invocations(invocations):
            inv = await asyncio.coroutine(v.__check__)(self, k)
            if inv:
                return inv[0], inv[1]
        raise UnfittedContext

    async def invoke(self):
        """
        Calls the invocation, if is None or any False value,
        will try to fit some invocation from self.bot.invocations
        """
        if not self.invocation:
            if not await asyncio.coroutine(self.bot.summoning)(self, self._message):
                return None
            path, invocation = await self.fit(self.bot.invocations)
            await self.load(path, invocation)
        return await asyncio.coroutine(self.invocation)(self)

    async def send(self, *args, **kwargs):
        """
        Its just a alias of channel.send,
        exists for extensions
        """
        return await self.channel.send(*args, **kwargs)

class KBot(discord.AutoShardedClient):
    def __init__(self, log_name='Kommando.py', owners=None):
        discord.AutoShardedClient.__init__(self)
        
        self.Kontext = deepcopy(Kontext)
        self.log = logging.getLogger(type(self).__name__)
        self.log.setLevel(logging.DEBUG)

        self.owners = owners or []
        self.summoning = None
        self.invocations = {}
        self.error_handler = None

    def kontext(self, message, cls=None):
        if not cls:
            return self.Kontext(self, message)
        else:
            return cls(self, message)
        
    # Invocation decorator

    def get_invocation(self, query, root=None):
        if root == None:
            root = self.invocations
        for x in query.split('/'):
            root = root[x]
        return root

    def remove_invocation(self, query:str):
        self.get_invocation(query).bot = None
        data = query.rsplit('/', 1)
        if len(data) == 1:
            del self.invocations[data[0]]
        else:
            query, key = data
            del self.get_invocation(query)[key]

    def walk_invocations(self, invocations=None, bfs=True):
        if invocations is None:
            invocations = self.invocations
        if bfs:
            deque = collections.deque(invocations.items())
            while True:
                try:
                    k, v = deque.popleft()
                    yield k, v
                    if hasattr(v, '__nodes__'):
                        nodes = v.__nodes__(self, k).items()
                        deque.extend([(k, v) for k, v in nodes
                                    if (k, v) not in deque])
                except IndexError:
                    raise StopIteration
        else:
            for k, v in invocations.items():
                yield k, v
                if hasattr(v, '__nodes__'):
                    nodes = v.__nodes__(self, k)
                    yield from self.walk_invocations(invocations=nodes, 
                                                     bfs=bfs)

    def invocation(self, template, root=None, **kwargs):
        """
        Decorator for creating invocations, 
        uses a function and a Template class

        Kwargs are used as invocation instance
        variables
        """
        def decorator(f):
            frame = inspect.currentframe().f_back
            extension = inspect.getmodule(frame)
            extension = extension.__name__ if extension is not None else '__main__'
            section = inspect.getframeinfo(frame).function
            defaults = {'id': f.__name__ if hasattr(f, '__name__') else None, 
                        'extension': extension, 'section': section,
                        'function': f, 'stats': {}, 'bot': self}
            invocation = template(**{**defaults, **kwargs})
            if root:
                self.get_invocation(root)[invocation.id] = invocation
            else:
                self.invocations[invocation.id] = invocation
            return invocation
        return decorator

    # Parse functions

    async def parse_message(self, message):
        """
        Takes the message and try to see if
        its context fit to an invocation

        If fits, the invocation is called
        """
        ktx = self.kontext(message)
        try:
            return await ktx.invoke()
        except Exception as e:
            if self.error_handler:
                await asyncio.coroutine(self.error_handler)(ktx, e)
            else:
                raise e
