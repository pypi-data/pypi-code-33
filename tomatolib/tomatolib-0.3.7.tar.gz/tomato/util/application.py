#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import signal
import asyncio
import logging
import functools
from tomato.util.appmodule import AppModule
from tomato.util.singleton import singleton
from tomato.util.typeassert import typeassert


@singleton
class Application(object):

    def __init__(self, *args, **kwargs):
        self.__running = False
        self.__modules = {}
        self.__module_names = []

    async def __func_call(self, func):
        iscoroutine = asyncio.iscoroutinefunction(func)
        if iscoroutine:
            await func()
        else:
            func()

    async def __run(self):
        self.__running = True
        try:
            for name in self.__module_names:
                module = self.__modules[name]
                await self.__func_call(module.setup)
                await self.__func_call(module.run)
        except Exception as e:
            logging.exception(e)
            try:
                await self.__destroy()
            finally:
                sys.exit(1)

    async def __destroy(self):
        for name in self.__module_names:
            module = self.__modules[name]
            await self.__func_call(module.destroy)
        self.__running = False
        logging.info('server has stopped')

    def __add_signal(self, future, loop):
        def shutdown(signame, future, loop):
            logging.warning('got signal %s: server is about to stop', signame)
            future.cancel() # TODO  if the outer Future is cancelled, all children (that have not completed yet) are also cancelled.
            loop.stop()
        loop.add_signal_handler(signal.SIGINT, functools.partial(shutdown, 'SIGINT', future, loop))
        loop.add_signal_handler(signal.SIGHUP, functools.partial(shutdown, 'SIGHUP', future, loop))
        loop.add_signal_handler(signal.SIGTERM, functools.partial(shutdown, 'SIGTERM', future, loop))

    def run(self):
        if self.__running:
            logging.warning('application already running')
            return

        loop = asyncio.get_event_loop()
        future = asyncio.gather(self.__run())
        self.__add_signal(future, loop)
        loop.run_until_complete(future)

    def stop(self):
        if self.__running:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.__destroy())

    def run_forever(self):
        if self.__running:
            logging.warning('application already running')
            return

        loop = asyncio.get_event_loop()
        future = asyncio.gather(self.__run())
        self.__add_signal(future, loop)
        loop.run_until_complete(future)
        loop.run_forever()
        loop.run_until_complete(self.__destroy())

    def add_module(self, name, module):
        if self.__running:
            logging.error('application running, cannot add module[%s]', name)
            return

        if name in self.__modules:
            logging.warning('[%s] module with the same name already exists', name)
            return

        self.__module_names.append(name)
        self.__modules[name] = module

    def get_module(self, name):
        return self.__modules.get(name, None)

    def print_modules(self):
        logging.info(self.__modules)

    def __getitem__(self, name):
        return self.get_module(name)

    def __setitem__(self, name, module):
        self.add_module(name, module)
