#!/usr/bin/env python3


import aioredis
import asyncio
import functools
import json
from signal import signal, SIGTERM, SIGINT
import sys
import traceback
import time


class GVApplication:

    def __init__(self, logger):
        self.logger = logger
        self.logger.info('Starting application...')

        self.isstopping = False
        self.loop = None
        self.redispool = None

    def init_from_thread(self, loop, redisaddr):
        self.__set_loop(loop)
        self.__set_redispool(redisaddr)

    def __set_loop(self, loop):
        self.loop = loop
        asyncio.set_event_loop(self.loop)

    def __set_redispool(self, redisaddr):
        if self.loop is None:
            self.logger.error('No event loop. return.')
            return

        try:
            self.redispool = self.loop.run_until_complete(
                aioredis.create_redis_pool(redisaddr, encoding='utf-8', loop=self.loop, minsize=5, maxsize=10)
            )
            self.logger.debug('Connected to Redis server.')
        except asyncio.TimeoutError:
            self.logger.warning('Unable to connect to the Redis server.')

    def run(self):
        if self.loop is None:
            self.logger.error('No event loop. return.')
            return

        self.loop.call_soon(functools.partial(self.logger.info, 'RpcClient started.'))
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.__clean())
            self.__close_loop()
        self.logger.info('RpcClient stopped.')

    async def add_callback(self, channelname, callback):
        while self.redispool is not None and not self.redispool.closed and not self.isstopping:
            channel = (await self.redispool._subscribe(channelname))[0]
            while await channel.wait_message():
                data = (await channel.get_json()).get('data')
                asyncio.ensure_future(callback(data))
        self.logger.warning('RpcClient has stopped to listen Redis channel:' + str(channelname))

    async def publish(self, channelname, data):
        if self.redispool is not None:
            message = await self.loop.run_in_executor(None,
                                                      functools.partial(json.dumps,
                                                                        {'data': data}, separators=(',', ':')))
            await self.redispool.publish(channelname, message)

    def stop(self):
        self.logger.info('Stopping application...')
        self.isstopping = True
        if self.redispool is not None:
            self.__stop_redis()
        if self.loop is not None:
            self.__stop_loop()

    def __stop_redis(self):
        self.logger.debug('Closing Redis connections...')
        self.redispool.close()

    def __stop_loop(self):
        self.logger.debug('Stopping event loop...')
        self.loop._cancel()

    async def __clean(self):
        if self.redispool is not None:
            await self.__wait_redis()
        await self.__wait_tasks()

    async def __wait_redis(self):
        await asyncio.shield(asyncio.wait_for(self.redispool.wait_closed(), timeout=5))
        self.logger.debug('Redis connections closed.')

    async def __wait_tasks(self):
        await asyncio.shield(asyncio.wait(asyncio.Task.all_tasks(), timeout=5))

    def __close_loop(self):
        self.logger.debug('Event loop stopped.')
        self.logger.debug('Closing event loop...')
        self.loop.close()
        self.logger.debug('Event loop closed.')

    def __serialiaze_json(self, obj):
        try:
            return obj.isoformat()
        except ValueError:
            self.logger.error(traceback.format_exc())
            self.logger.error('Unable to serialize obj: ' + str(obj))
            return None


def run_in_thread(application, redisaddr):
    application.init_from_thread(asyncio.new_event_loop(), redisaddr)


def stop(application):
    application.loop.call_soon_threadsafe(application._cancel)
    while application.loop.is_running():
        time.sleep(0.1)


# Register signals handler
signal(SIGTERM, lambda signum, stack_frame: sys.exit(1))
signal(SIGINT, lambda signum, stack_frame: sys.exit(1))
