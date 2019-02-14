# coding=utf-8
from __future__ import print_function

import time
import traceback

import redis


class RedisMStorage(object):
    def __init__(
        self, redisHost="localhost", redisPort=6379, options=None, client=None, **kwargs
    ):
        self.options = options or {}
        self.options.update(host=redisHost, port=redisPort)
        if client and not isinstance(client, redis.Redis):
            raise Exception("Invalid client: {}".format(client))
        self.client = client or redis.Redis(
            host=self.options["host"], port=self.options["port"]
        )

    def type(self, name):
        return self.client.type(name)

    def exists(self, *names):
        return self.client.exists(*names)

    def expire(self, name, expire):
        return self.client.expire(name, expire)

    def delete(self, *names):
        return self.client.delete(*names)

    def get(self, name):
        return self._kget(name)

    def set(self, name, value, *args, **kwargs):
        return self._kset(name, value, *args, **kwargs)

    def mget(self, name):
        return self._hmgetall(name)

    def mset(self, name, mapping):
        return self._hmset(name, mapping)

    def _kget(self, name):
        return self.client.get(name)

    def _kset(self, name, value, expire=None):
        return self.client.set(name, value, ex=expire)

    def _lset(self, name, value, expire=None):
        return self.client.lset(name)

    def _hmget(self, name, keys=None):
        return self._hmgetfields(name, keys) if keys else self._hmgetall(name)

    def _hmgetall(self, name):
        return self.client.hgetall(name)

    def _hmgetfields(self, name, keys):
        return dict(zip(keys, self.client.hmget(name, keys)))

    def _hmset(self, name, mapping):
        return self.client.hmset(name, mapping)
