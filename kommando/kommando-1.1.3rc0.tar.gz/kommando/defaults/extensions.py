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

from kommando.defaults.errors import DependencyError

def KTasks(bot):
    import asyncio

    class Tasks:
        def __init__(self, bot):
            self.bot = bot
            self.dict = {}

        def get_scheduler(self, name):
            async def _scheduler(*args, **kwargs):
                await self.bot.wait_until_ready()
                for task in self.dict[name]:
                    if await asyncio.coroutine(task)(*args, **kwargs):
                        return
            _scheduler.__name__ = name
            return _scheduler

        def new(self, event, pos=1, allow_multiple=False):
            def decorator(f):
                if event in self.dict:
                    if (not allow_multiple) and f in self.dict[event]:
                        pass
                    else:
                        self.dict[event].insert(pos, f)
                else:
                    self.bot.event(self.get_scheduler(event))
                    self.dict[event] = [f]
                async def decorated(*args, **kwargs):
                    return await f(args, kwargs)
                return decorated
            return decorator

        def end(self, f):
            for event in self.dict:
                for n, x in enumerate(self.dict[event]):
                    if x == f:
                        del self.dict[event][n]
                        return True

    bot.tasks = Tasks(bot)
    yield 'Loaded'

    del bot.tasks
    yield 'Unloaded'

def LiveObjects(bot):
    import json
    import time
    import asyncio
    import inspect
    import textwrap

    ARG_EXCLUDE = ['self', 'bot', 'cls']

    def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False

    def is_storable(lo):
        try:
            args = [k for k, v in inspect.signature(type(lo).__init__).parameters.items() 
                    if v.default is v.empty and k not in ARG_EXCLUDE]
            return all([is_jsonable(getattr(lo, x)) for x in args])
        except AttributeError:
            return False
            
    class Lo:
        def __init__(self, bot):
            self.bot = bot
            self.dict = {}
            self.models = {}

        def register(self, events, lo):
            now = time.time()
            lo.__stats__ = {'events': events, 'start_time': now, 'uses': []}
            lo.__model__ = type(lo).__name__
            if lo.__model__ not in self.models:
                self.models[lo.__model__] = type(lo)

            self.dict[id(lo)] = lo

            for event in events:
                handler = self.handler(event)
                handler.__name__ = 'lo_handler'

                if event in self.bot.tasks.dict:
                    check = filter(lambda x: x.__name__ == handler.__name__, 
                                   self.bot.tasks.dict[event])
                    if next(check, None):
                        continue
                self.bot.tasks.new(event)(handler)

        def handler(self, event):
            async def _handler(*args):
                for obj_id in reversed(list(self.dict)):
                    lo = self.dict[obj_id]
                    if event in lo.__stats__['events']:
                        if await asyncio.coroutine(lo.__check__)(args):
                            lo.__stats__['uses'].append(time.time())
                            await asyncio.coroutine(lo.__callback__)(args)
            return _handler

        def kill(self, object_id):
            del self.dict[object_id]

        def loads(self, slo_dict):
            if '__model__' not in slo_dict:
                raise KeyError('LO stored without an model')

            try:
                model = self.models[slo_dict['__model__']]
            except KeyError:
                raise KeyError(f'LO respective model not found: {slo_dict.__model__}')
            
            args = [k for k, v in inspect.signature(model.__init__).parameters.items()]
            missing = all([x in ARG_EXCLUDE for x in args if not hasattr(slo_dict, x)])
            if missing:
                raise AttributeError('Not all needed attributes are in the dict')
            kwargs = {x: slo_dict[x] for x in args 
                    if x not in ARG_EXCLUDE and x in slo_dict}
            if 'bot' in args:
                kwargs['bot'] = self.bot
            lo = model(**kwargs)
            for k, v in slo_dict.items():
                if not hasattr(lo, k):
                    setattr(lo, k, v)
            return lo
            
        def dumps(self, lo):
            if is_storable(lo):
                return {k:v for k, v in lo.__dict__.items() if is_jsonable(v)}
            else:
                raise TypeError(f'This instance of {type(lo).__name__} is not storable')

        async def slo_parse(self, var):
            if type(var) == str:
                if var.endswith('}'):
                    if var.startswith('&{'):
                        code = f'async def f():\n {textwrap.indent(var[2:-1], "  ")}\n'
                        env = {**globals(), **locals()}
                        exec(code, env)
                        var = await env['f']()
                    elif var.startswith('%{'):
                        var = eval(var[2:-1])
                        if asyncio.iscoroutine(var):
                            var = await var
            elif isinstance(var, dict):
                var = {**var}
                for k, v in var.items():
                    var[k] = await self.slo_parse(v)
            elif isinstance(var, list):
                var = [x for x in var]
                for n, x in enumerate(var):
                    var[n] = await self.slo_parse(x)
            return var
 
    bot.lo = Lo(bot)
    yield 'Loaded'

    del bot.lo
    yield 'Unloaded'

def LoPaginators(bot):
    import asyncio
    import discord

    if not hasattr(bot, 'lo'):
        raise DependencyError('LiveObjects')

    class Paginator:
        def __init__(self, bot, msg, user, iterable, reactions=None, callback=None):
            self.bot = bot

            self.it = 0
            self.msg = msg
            self.user = user
            self.iterable = iterable

            self.default = {'back': '⬅', 'confirm': '✅', 'next': '➡', 'exit': '❌'}
            self.reactions = reactions or self.default

            if callback is None:
                self.callback = lambda _: None
        
        async def prepare(self):
            await self.msg.edit(**self.iterable[0])
            await self.react()

        async def react(self):
            for x in list(self.reactions):
                if x not in self.reactions:
                    self.reactions[x] = None

            for v in self.reactions.values():
                if v is not None:
                    await self.msg.add_reaction(v)

        async def __check__(self, payload):
            payload = payload[0]
            user_id = payload.user_id
            if user_id == self.bot.user.id:
                return False
            if self.user is None:
                user_check = True
            elif type(self.user) in (tuple, set, list):
                user_check = user_id in self.user
            else:
                user_check = user_id == self.user
            msg_check = payload.message_id == self.msg.id
            reaction_check = str(payload.emoji) in self.reactions.values()
            return reaction_check and msg_check and user_check

        async def __callback__(self, payload):
            res = str(payload[0].emoji)
            if res == self.reactions['back']:
                self.it -= 1
            elif res == self.reactions['next']:
                self.it += 1
            elif res == self.reactions['exit']:
                await self.msg.delete()
                self.bot.lo.kill(id(self))
                return
            elif res == self.reactions['confirm']:
                self.bot.lo.kill(id(self))
                try:
                    await self.msg.clear_reactions()
                except discord.Forbidden:
                    for x in self.reactions.values():
                        await self.msg.remove_reaction(x, self.bot.user)
                choice = self.iterable[self.it]
                await asyncio.coroutine(self.callback)(choice)
                return
            try:
                if self.it >= len(self.iterable):
                    self.it = 0
                elif self.it < 0:
                    self.it = len(self.iterable) - 1
            except TypeError:
                pass
            await self.msg.edit(**self.iterable[self.it])

    class StorablePaginator(Paginator):
        def __init__(self, bot, msg_id, user, iterable, reactions=None, callback=None):
            self.bot = bot
            self.__storable__ = False

            self.it = 0
            self.msg_id = msg_id
            self.user = user

            self.iterable = iterable

            self.default = {'back': '⬅', 'confirm': '✅', 'next': '➡', 'exit': '❌'}
            self.reactions = reactions or self.default

            if callback is None:
                self.callback = lambda _: None

        async def prepare(self):
            channel, msg = self.msg_id.split('.')
            self.msg = await self.bot.get_channel(int(channel)).get_message(int(msg))

            it = await self.bot.lo.slo_parse(self.iterable)
            await self.msg.edit(**it[0])
            await self.react()

    async def lo_paginator(self, msg, user, iterable, reactions=None, **kwargs):
        lo = Paginator(self.bot, msg, user, iterable, reactions=reactions)
        await lo.prepare()
        self.bot.lo.register(('on_raw_reaction_add', 'on_raw_reaction_remove'), lo)
        return id(lo)

    async def slo_paginator(self, msg, user, iterable, reactions=None, **kwargs):
        msg = f'{msg.channel.id}.{msg.id}'
        lo = StorablePaginator(self.bot, msg, user, iterable, reactions=reactions)
        await lo.prepare()
        self.bot.lo.register(('on_raw_reaction_add', 'on_raw_reaction_remove'), lo)
        return id(lo)
 
    bot.lo.models['Paginator'] = Paginator
    bot.lo.models['StorablePaginator'] = StorablePaginator
    bot.Kontext.lo_paginator = lo_paginator
    bot.Kontext.slo_paginator = slo_paginator
    yield 'Loaded'

    try:
        del bot.lo.models['Paginator']
        del bot.lo.models['StorablePaginator']
    except AttributeError:
        pass
    del bot.Kontext.lo_paginator
    del bot.Kontext.slo_paginator
    yield 'Unloaded'

def Debug(bot):
    if not hasattr(bot, 'lo'):
        raise DependencyError('LiveObjects')

    import ast
    import asyncio
    import inspect
    import textwrap
    from io import StringIO
    from traceback import format_exc
    from contextlib import redirect_stdout
    from kommando.defaults import types, modifiers, templates

    bot.invocation(templates.Container, id='__Debug__')(None)

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    wrapper = textwrap.TextWrapper(width=100, replace_whitespace=False)
    async def send_console(ktx, text, title='', sanitize=True, lines=15):
        if sanitize:
            splitted = wrapper.wrap(text)
        else:
            splitted = text.splitlines()
        result = []
        lines = [x for x in chunks(splitted, lines)]
        for n, x in enumerate(lines):
            x = [f'{title} - Page - {n+1}/{len(lines)}', ''] + x
            result.append({'content': f"```" + '\n'.join(x) + "```"})
        if len(result) > 1:
            msg = await ktx.send('...')
            await ktx.lo_paginator(msg, ktx.author.id, result)
        else:
            await ktx.send(result[0]['content'])

    @bot.invocation(templates.Command, root='__Debug__')
    @modifiers.owner_only
    async def execute(ktx, code:types.Unsplitted):
        code = ''.join(code)
        if code.startswith('```') and code.endswith('```'):
            code ='\n'.join(code.split('\n')[1:-1])
        env = {}
        stdout, stderr, ret = StringIO(), '', ''
        code = f'async def f(bot, ktx):\n{textwrap.indent(code, "    ")}'
        await ktx.message.add_reaction('🐍')
        try:
            with redirect_stdout(stdout):
                exec(code, env)
                ret = await env['f'](bot, ktx)
        except:
            stderr = format_exc()
        stdout = stdout.getvalue()
        if stdout:
            await send_console(ktx, stdout, title='Stdout')
        if ret:
            await send_console(ktx, repr(ret), title='Return')
        if stderr:
            await send_console(ktx, stderr, title='Stderr', 
                               sanitize=False, lines=10)

    class DebuggerLO:
        def __init__(self, ktx, msg, user, lines, generator, endpoints):
            self.ktx = ktx

            self.it = 0
            self.msg = msg
            self.user = user
            self.lines = lines
            self.generator = generator
            self.endpoints = endpoints

        async def prepare(self):
            await self.msg.add_reaction('▶')

        def __check__(self, payload):
            payload = payload[0]
            if str(payload.emoji) != '▶':
                return False
            user_id = payload.user_id
            if user_id == bot.user.id:
                return False
            ucheck = True if self.user is None else user_id == self.user.id
            return (payload.message_id == self.msg.id) and ucheck

        async def __callback__(self, payload):
            msg = self.msg
            output = StringIO()
            end = False
            try:
                ln = -1
                g = self.generator
                with redirect_stdout(output):
                    try:
                        ln = await g.__anext__()
                        if ln in self.endpoints:
                            end = True
                    except StopAsyncIteration:
                        end = True
                    except:
                        await send_console(self.ktx, format_exc(), 
                                           title='Stderr')
                        end = True
                stdout = output.getvalue()
                l = self.lines[:]
                l[ln] = f'{l[ln]} <<-----'
                code = '\n'.join(l)
                if g.ag_frame is None:
                    raise StopAsyncIteration
                env = '\n'.join([f'{k}: {v}' for k, v in g.ag_frame.f_locals.items()])
                self.it += 1
                code = f'```python\n{code}\n```'
                env = f'```python\n{env}```'
                stdout = f'```python\nOutput: {stdout}```'
                
                await msg.edit(content= '\n'.join([code, env, stdout]))

                if end:
                    raise StopAsyncIteration
            except StopAsyncIteration:
                await msg.remove_reaction('▶', bot.user)
                bot.lo.kill(id(self))

    @bot.invocation(templates.Command, root='__Debug__')
    @modifiers.owner_only
    async def debug(ktx, code:types.Unsplitted):
        code = ''.join(code)
        if code.startswith('```') and code.endswith('```'):
            code ='\n'.join(code.split('\n')[1:-1])
        env = {}
        code = f'async def f(bot, ktx):\n{textwrap.indent(code, "    ")}'
        await ktx.message.add_reaction('🐍')
        await debugger(ktx, code, 'f', env)

    class Yieldifier(ast.NodeTransformer):
        def __init__(self):
            ast.NodeTransformer.__init__(self)

        def generic_visit(self, node):
            ast.NodeTransformer.generic_visit(self, node)
            if isinstance(node, ast.stmt):
                return [node, ast.Expr(value=ast.Yield(value=ast.Num(n=node.lineno - 1)))]
            else:
                return node

    async def debugger(ktx, code, fname, env, *args, **kwargs):
        code = code.split('\n')
        astcode = code[:]

        endpoints = []
        for n, x in enumerate(astcode):
            if x.lstrip().startswith('return'):
                astcode[n] = f'{astcode[n].replace("return", "print(", 1)})'
                endpoints.append(n)
                
        astcode = '\n'.join(astcode)

        tree =  ast.parse(astcode)
        func_tree = tree.body[0]
        Yieldifier().visit(func_tree)
        ast.fix_missing_locations(func_tree)

        exec(compile(tree, '<ast>', 'exec'), env)
        ret = env[fname](bot, ktx, *args, **kwargs)

        await ktx.message.add_reaction('🐍')
        try:
            msg = await ktx.send('Press ▶️ to debug!')
            lo = DebuggerLO(ktx, msg, ktx.author, code, ret, endpoints)
            await lo.prepare()
            events = ('on_raw_reaction_add', 'on_raw_reaction_remove')
            bot.lo.register(events, lo)
        except Exception:
            await send_console(ktx, format_exc())
    yield 'Loaded'

    bot.remove_invocation('__Debug__')
    yield 'Unloaded'

def SlowWriting(bot):  
    import time
    import asyncio

    def decorate(f):
        async def send(self, *args, **kwargs):
            if self.bot.WPM is not None:
                length = 0
                if 'content' in kwargs:
                    length += len(kwargs['content'])
                for x in args:
                    length += len(x)
                seconds = ((length/5) * 60)/self.bot.WPM
                async with self.channel.typing():
                    if self.bot.async_typing:
                        await asyncio.sleep(seconds)
                    else:
                        time.sleep(seconds)
            return await f(self, *args, **kwargs)
        return send

    bot.WPM = None
    bot.async_typing = True
    send = bot.Kontext.send
    bot.Kontext.send = decorate(bot.Kontext.send)
    yield 'Loaded'

    del bot.WPM
    del bot.async_typing
    bot.Kontext.send = send
    yield 'Unloaded'

def NaturalResponse(bot):
    import random

    def response(self, s, *args, **kwargs):
        default = []
        extension_specific = []
        invocation_specific = []

        trdata = self.bot.dictionary

        if 'defaults' in trdata:
            default = trdata['defaults']

        if 'specific' in trdata:
            specific = trdata['specific']
            if self.extension in specific:
                extension = specific[self.extension]
                if '__defaults__' in extension:
                    extension_specific = extension['__defaults__']
                if self.invocation.id in extension:
                    invocation_specific = extension[self.invocation.id]

        if s in invocation_specific:
            r = invocation_specific[s]
        elif s in extension_specific:
            r = extension_specific[s]
        elif s in default:
            r = default[s]
        else:
            r = None
        
        def parse(r):
            if type(r) == str:
                return r.format(*args, **kwargs)
            elif type(r) in (tuple, list):
                return random.choice(r).format(*args, **kwargs)
            elif type(r) is dict:
                for x in self.bot.emotional_state:
                    if x in r:
                        return parse(r[x])

        if r is None:
            r = bot.default_response
        else:
            r = parse(r)
            if self.bot.response_modifier is not None:
                r = self.bot.response_modifier(self, r)
        return r

    async def send_response(self, s, *args, **kwargs):
        return await self.send(self.response(s, *args, **kwargs))

    bot.default_response = '...'
    bot.response_modifier = None
    bot.dictionary = {}
    bot.emotional_state = ['normal'] 
    bot.Kontext.response = response
    bot.Kontext.send_response = send_response
    yield 'Loaded'

    del bot.default_response
    del bot.response_modifier
    del bot.dictionary
    del bot.emotional_state
    del bot.Kontext.response
    del bot.Kontext.send_response
    yield 'Unloaded'

def Translation(bot): 
    import copy
    import asyncio
    import gettext
    from types import MethodType
    from functools import lru_cache
    from kommando.base import UnfittedContext

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if type(attr) is str:
            try:
                return object.__getattribute__(self, 'language')(attr)
            except AttributeError:
                return attr
        else:
            return attr

    @lru_cache()
    async def translate(ktx, v):
        v = copy.copy(v)
        v.language = await asyncio.coroutine(ktx.bot.language)(ktx)
        type(v).__getattribute__ = __getattribute__
        return v

    async def fit(self, invocations):    
        """
        (Translation Version)

        Iterates over all invocations to find 
        whose fits the ctx, using __check__
        __check__ needs to return a Class or a false value

        Returns a path and a invocation
        """
        for k, v in self.bot.walk_invocations(invocations):
            v = await translate(self, v)
            inv = await asyncio.coroutine(v.__check__)(self, k)
            if inv:
                return inv[0], await translate(self, inv[1])
        raise UnfittedContext

    bot.language = lambda ktx: gettext.gettext
    old_fit = bot.Kontext.fit
    bot.Kontext.fit = fit
    yield 'Loaded'
    del bot.language 
    bot.Kontext.fit = old_fit
    yield 'Unloaded'
