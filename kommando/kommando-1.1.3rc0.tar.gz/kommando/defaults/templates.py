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

import re
import copy
import random
import asyncio
import discord
import gettext
import inspect

from functools import lru_cache
from itertools import takewhile, dropwhile, tee
from typing import Iterable, Tuple, Union, Callable

from kommando.base import UnfittedContext
from kommando.defaults.errors import ParsingError
from kommando.defaults.types import SpecialType, _PassContext

def _common_split(text:str) -> Tuple[Iterable, Iterable]:
    '''Splits a string in a shlex like way,
    preserving whitespaces inside quotes, but
    allowing open quotes
    
    Parameters:
        text: the string you need to split
    
    Returns:
        A tuple, containing a copy of the cached generator
        and a iterator of the text
    '''
    text = iter(text)
    def _splitter(text):
        while True:
            try:
                n = next(text)
                l = takewhile(lambda x: (x != n) if n == '"' else x.strip(), text)
                l = (n if n != '"' else '') + ''.join(list(filter(lambda x: x != '"', l)))
                if l.strip():
                    yield l
            except StopIteration:
                break
    return _splitter(text), text

def _parameters(f: Callable) -> Iterable[Tuple[str, inspect.Parameter]]:
    '''Get the parameters of a function, ignoring
    self, cls and ktx arguments
    
    Parameters:
        f: A function
    
    Returns:
        A iterable containing tuples (name, parameter)'''
    exclude = ['self', 'cls', 'ktx']
    _par = inspect.signature(f).parameters
    _par_list = filter(lambda x: x not in exclude, _par)
    return ((x, _par[x]) for x in _par_list)

class Common:
    def __init__(self, **kwargs):
        self.id, self.function = None, None
        self.scroll, self.stats = None, None
        self.root, self.bot = None, None
        self.aliases = []

        self.__dict__ = {**self.__dict__, **kwargs}
        
    async def arg_parser(self, ktx, hargs: Iterable, text:Iterable=None) \
                         -> Union[Tuple[list, dict], None]:
        '''
        Transforms a iterable of user args into specific args, kwargs, based
        of function parameters and typing

        If provides 
        
        Parameters:
            ktx : Default context class from kommando.py
            hargs: A iterable containing the human-readable args
            text: Optional, a iterable that is exausted by hargs iterable,
                  if not provided, some SpecialTypes cannot be used, like
                  Unsplitted

        Returns:
            A tuple containing a list(args) and a dict(kwargs), or None
        '''

        nms = {'hargs': hargs, 'text': text,
               'args': [], 'kwargs': {},
               'pars': _parameters(self.function)}
                
        def iterable(x):
            try:
                iter(x)
                return True
            except TypeError:
                return False

        async def parse(kind, ann, x=None):
            '''
            Try to convert a annotation from a parameter kind
            using the following logic:

            1. See if kind is *args like
            2. If not, try to convert in the following order
               - Annotation is callable
               - Annotation is iterable
               - The type of Annotation is callable
               - Unknown (returns without conversion)
            3. Else, exaust the hargs iterable on a list,
               if the annotation is not None, try to
               convert it (only callable here)
            '''
            if kind != 2: # not VAR_POSITIONAL
                if callable(ann):
                    if isinstance(ann, _PassContext):
                        x = x or next(nms['hargs'])
                        try:
                            return await asyncio.coroutine(ann)(ktx, x)
                        except:
                            raise ParsingError(2, x=x, ann=ann)
                    elif isinstance(ann, SpecialType):
                        try:
                            return await asyncio.coroutine(ann)(ktx, nms)
                        except:
                            raise ParsingError(3, ann=ann)
                    else:
                        x = x or next(nms['hargs'])
                        try:
                            return await asyncio.coroutine(ann)(x)
                        except:
                            raise ParsingError(4, x=x, ann=ann)
                elif iterable(ann):
                    x = x or next(nms['hargs'])
                    for a in iter(ann):
                        try:
                            return await parse(kind, a, x)
                        except:
                            pass
                    raise ParsingError(5, x=x, ann=ann)
                else:
                    return x or next(nms['hargs'])
            else:
                l = list(nms['hargs'])
                return [await parse(1, ann, x) for x in l] if ann else l

        for k, v in nms['pars']:
            try:
                kind = v.kind 
                ann = v.annotation if v.annotation is not v.empty else None
                if kind == 4: # VAR_KEYWORD
                    continue

                data = await parse(kind, ann)
                if kind == 1: # POSITIONAL_OR_KEYWORD
                    if v.default is v.empty: # POSITIONAL
                        nms['args'].append(data)
                    else: # KEYWORD
                        nms['kwargs'][k] = data
                elif kind == 2: # VAR_POSITIONAL
                    nms['args'].extend(data)
                elif kind == 3: # KEYWORD_ONLY
                    nms['kwargs'][k] = data
            except RuntimeError: # Few hargs
                if v.default is v.empty:
                    raise ParsingError(0)

        for k, v in nms['pars']: # Fill the empty keywords
            if k not in nms['kwargs']: #  No way to v.default be v.empty here
                nms['kwargs'][k] = v.default

        try:
            next(nms['hargs'])
            raise ParsingError(1)
        except StopIteration:
            return nms['args'], nms['kwargs'] # Success

class Container(Common):
    def __init__(self, **kwargs):
        self.sub_invocations = {}
        self.root = None
        super().__init__(**kwargs)
                      
    def __getitem__(self, k):
        return self.sub_invocations[k]

    def __setitem__(self, k, v):
        self.sub_invocations[k] = v

    def __delitem__(self, k):
        del self.sub_invocations[k]

    def __contains__(self, k):
        return k in self.sub_invocations

    def __len__(self):
        i = 0
        for v in self.sub_invocations.values():
            if hasattr(v, '__len__'):
                i += len(v)
            else:
                i += 1
        return i
        
    def __nodes__(self, _ktx, path):
        return {f'{path}/{k}': v for k, v in self.sub_invocations.items()}

    async def __check__(self, ktx, path):
        for k, v in self.bot.walk_invocations(self.sub_invocations):
            inv = await asyncio.coroutine(v.__check__)(ktx, k)
            if inv:
                path, inv = f'{path}/{inv[0]}', inv[1]
                if callable(self.function):
                    await asyncio.coroutine(self.function)(ktx, path, inv)
                return path, inv

class Group(Container):
    async def __call__(self, ktx):
        if callable(self.function):
            return await asyncio.coroutine(self.function)\
                         (ktx, ktx.path, self)

    async def __check__(self, ktx, path):
        g, text = _common_split(ktx._message.content)
        if next(g, None) in self.aliases + [self.id]:
            ktx._message.content = ''.join(text)
            try:
                inv = await ktx.fit(self.sub_invocations)
                path, inv = f'{path}/{inv[0]}', inv[1]
                if callable(self.function):
                    f = asyncio.coroutine(self.function)
                    await f(ktx, path, inv)
            except UnfittedContext:
                inv = self
            return path, inv

class Command(Common):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def __call__(self, ktx):
        hargs, text = _common_split(ktx._message.content)
        next(hargs)
        args, kwargs = await self.arg_parser(ktx, hargs, text=text)
        return await asyncio.coroutine(self.function)(ktx, *args, **kwargs)

    def __check__(self, ktx, path):
        name = next(_common_split(ktx._message.content)[0], None)
        if name in self.aliases + [self.id]:
            return path, self

class RegexCommand(Common):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'regex'):
            self.regex = None

    async def __call__(self, ktx):
        groups = re.match(self.regex, ktx._message.content).groupdict()
        pars = _parameters(self.function)
        args, kwargs = await self.arg_parser(ktx, map(lambda x: groups[x[0]], pars))
        return await asyncio.coroutine(self.function)(ktx, *args, **kwargs)

    def __check__(self, ktx, path):
        if not self.regex:
            ktx.logger.error(f"Invocation without regex!")
            return False
        if re.match(self.regex, ktx._message.content):
            return path, self

class Subliminal(Common):
    def __init__(self, **kwargs):
        self.regex = re.compile(r'\*\*([ A-z0-9]*)\*\*')
        super().__init__(**kwargs)

    async def __call__(self, ktx):
        hargs = (x[1] for x in self.regex.finditer(ktx._message.content))
        next(hargs, None)
        args, kwargs = await self.arg_parser(ktx, hargs)
        return await asyncio.coroutine(self.function)(ktx, *args, **kwargs)

    def __check__(self, ktx, path):
        try:
            x = next(self.regex.finditer(ktx._message.content))
            if x[1] in self.aliases + [self.id]:
                return path, self
        except StopIteration:
            pass
