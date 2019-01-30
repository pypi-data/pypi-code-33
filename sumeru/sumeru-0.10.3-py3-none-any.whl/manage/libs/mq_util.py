#! /usr/bin/env python
#coding=utf-8
from __future__ import print_function, division, absolute_import
import logging

import redis
import redislite

import asyncio
from aio_etcd import Client, EtcdKeyNotFound
from etcd import Client as ClientSync, EtcdKeyNotFound, Lock
ioloop = asyncio.get_event_loop()

logger = logging.getLogger(__name__)

def except_catcher(func):
    '''
    class to catch redis exception
    '''
    def d_func(*args, **kargs):
        try:
            return func(*args, **kargs)
        except Exception as e:
            logger.error('[-] %s ' % (e))
            return None

    return d_func

class RedisMQ(object):
    __instance = None

    def __new__(cls, *args, **kwd):

        if RedisMQ.__instance is None:
            RedisMQ.__instance = object.__new__(cls, *args, **kwd)

            try:
                cls.client = redis.Redis().from_url(__sumeru__.REDIS_DRIVER)
            except Exception as e:
                logger.warning(e)
                #cls.client = redislite.Redis().from_url('/tmp/redis.db')

        return RedisMQ.__instance

    @except_catcher
    def switch(cls):
        if not hasattr(__sumeru__, 'REDIS_DRIVER'): return
        cls.client = redis.Redis().from_url(__sumeru__.REDIS_DRIVER)

    @except_catcher
    def flush(self):
        return self.client.flushdb()

    @except_catcher
    def pop(self, key):
        return self.client.rpop(key)

    @except_catcher
    def push(self, key, value):
        return self.client.lpush(key, value)

    @except_catcher
    def lpush(self, key, value):
        return self.client.lpush(key, value)

    @except_catcher
    def rpush(self, key, value):
        return self.client.rpush(key, value)

    @except_catcher
    def pub(self, key, value):
        return self.client.publish(key, value)

    @except_catcher
    def get(self, key):
        return self.client.get(key)

    @except_catcher
    def set(self, key, value):
        return self.client.set(key, value)

    @except_catcher
    def inc(self, key):
        return self.client.incr(key)


class HA_ETCD(object):
    __instance = None

    def __new__(cls, *args, **kwd):

        if HA_ETCD.__instance is None:
            HA_ETCD.__instance = object.__new__(cls, *args, **kwd)

            try:
                cls.client = Client(host=tuple(eval(__sumeru__.ETCD_DRIVER)), \
                                    allow_reconnect=True, loop = ioloop)
            except Exception as e:
                logger.warning(e)

        return HA_ETCD.__instance

    def switch(cls):
        if not hasattr(__sumeru__, 'ETCD_DRIVER'): return
        cls.client = Client(host=tuple(eval(__sumeru__.ETCD_DRIVER)), \
                            allow_reconnect=True, loop = ioloop)

    async def write(self, key, value, **kwargs):
        return await self.client.write(key, value, **kwargs)

    async def read(self, key, **kwargs):
        try:
            return await self.client.read(key, **kwargs)
        except EtcdKeyNotFound as e:
            return None

    async def delete(self, key, **kwargs):
        try:
            await self.client.delete(key, **kwargs)
        except EtcdKeyNotFound as e:
            pass


class HA_ETCD_SYNC(object):
    __instance = None

    def __new__(cls, *args, **kwd):

        if HA_ETCD_SYNC.__instance is None:
            HA_ETCD_SYNC.__instance = object.__new__(cls, *args, **kwd)

            try:
                cls.client = ClientSync(host=tuple(eval(__sumeru__.ETCD_DRIVER)), \
                                    allow_reconnect=True)
            except Exception as e:
                logger.warning(e)

        return HA_ETCD_SYNC.__instance

    def switch(cls):
        if not hasattr(__sumeru__, 'ETCD_DRIVER'): return
        cls.client = ClientSync(host=tuple(eval(__sumeru__.ETCD_DRIVER)), \
                                allow_reconnect=True)

    def lock(self, name):
        return Lock(self.client, name)

    def write(self, key, value, **kwargs):
        return self.client.write(key, value, **kwargs)

    def read(self, key, **kwargs):
        try:
            return self.client.read(key, **kwargs)
        except EtcdKeyNotFound as e:
            return None

    def delete(self, key, **kwargs):
        try:
            self.client.delete(key, **kwargs)
        except EtcdKeyNotFound as e:
            pass
