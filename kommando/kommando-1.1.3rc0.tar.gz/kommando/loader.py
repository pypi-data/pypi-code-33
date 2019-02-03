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

import os
import sys
import asyncio
import inspect
import importlib
import traceback

from itertools import tee
from collections import namedtuple

class Loader:
    def __init__(self, bot):
        self.bot = bot
        self.dict = {}
    
    def add(self, module):
        ref = importlib.import_module(module)
        self.dict[ref.__name__] = {'ref': ref, 'sections': {}}

    def remove(self, module):
        for x in self.dict[module]['sections']:
            self.switch_until_finished(module, x)
        del self.dict[module]

    def reload(self, module):
        ref = self.dict[module]['ref']
        self.remove(module)
        ref = importlib.reload(ref)
        self.dict[ref.__name__] = {'ref': ref, 'sections': {}}

    def from_folder(self, path, ignore=None, switch=1):
        ignore = ignore or []
        if path not in sys.path:
            sys.path.insert(1, path)

        for x in os.listdir(path):
            hidden = x.startswith('__') and x.endswith('__')
            python = x.endswith('.py')
            if not hidden and python:
                x = x.rsplit('.py', 1)[0]
                if x not in ignore:
                    self.add(x)
                    for y in dir(self.dict[x]['ref']):
                        self.load_section(x, y, switch=switch)
    
    def from_list(self, extensions, switch=1):
        for x in extensions:
            self.add(x)
            for y in dir(self.dict[x]['ref']):
                self.load_section(x, y, switch=switch)
    
    def load_section(self, module, section, switch=1):
        data = self.dict[module]
        ref = data['ref']
        x = getattr(ref, section)
        if inspect.isgeneratorfunction(x):
            if x.__module__ == ref.__name__:
                s = data['sections'][x.__name__] = {}
                s['function'] = x
                s['generator'] = x(self.bot)
                s['state'] = None
                self.bot.log.info(f'Section {section} from {module} load')
                self.switch(module, section, times=switch)
                return True
        return False

    def load_sections(self, module, switch=1):
        for x in dir(self.dict[module]['ref']):
            self.load_section(module, x, switch=switch)

    def switch(self, module, section, times=1, reset=True):
        if times > 0:
            for _ in range(times):
                s = self.dict[module]['sections'][section]
                try:
                    s['state'] = next(s['generator'])
                except StopIteration:
                    if reset:
                        s['generator'] = s['function'](self.bot)
                        s['state'] = next(s['generator'])
                    else:
                        raise StopIteration
            self.bot.log.info(f'{module}/{section} state changed to {s["state"]}')
            return s["state"]

    def switch_until_state(self, module, section, state, max_tries=10, skip=0):
        s = self.dict[module]['sections'][section]
        i = 0
        for _ in range(skip):
            self.switch(module, section)
            max_tries -= 1
        while s['state'] != state:
            self.switch(module, section)
            if i >= max_tries:
                break
            i += 1
        return s['state'] == state

    def switch_until_finished(self, module, section):
        while True:
            try:
                self.switch(module, section, reset=False)
            except StopIteration:
                break

    def get_state(self, module, section):
        return self.dict[module]['sections'][section]['state']
    
    def get_vars(self, module, section):
        frame = self.dict[module]['sections'][section]['generator'].gi_frame
        return frame.f_globals, frame.f_locals

async def watcher(self):
    dates = {}
    while True:
        for k,v in {**self.loader.dict}.items():
            f = v['ref'].__file__
            md = os.stat(f).st_mtime
            if f in dates:
                if dates[f] < md:
                    sections = [(k, v['state']) 
                                for k,v in v['sections'].items()]
                    try:
                        self.loader.reload(k)
                        for x in sections:
                            self.loader.load_section(k, x[0], switch=0)
                            self.loader.switch_until_state(k, x[0], x[1])
                        dates[f] = md
                    except:
                        traceback.print_exc()
            else:
                dates[f] = md
        await asyncio.sleep(1)

def install(bot):
    bot.extensions = []
    bot.loader = Loader(bot)

def watch(bot):
    bot.loop.create_task(watcher(bot))
