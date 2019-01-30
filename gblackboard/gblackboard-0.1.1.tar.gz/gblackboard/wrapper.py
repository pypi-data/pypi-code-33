# -*- coding: utf-8 -*-

import abc
import enum
import json
import redis
import socket

from .data import Data
from .exception import *


DEV_MODE = False


class SupportedMemoryType(enum.Enum):

    """
    Supported memory type.
    """

    DICTIONARY = 0
    REDIS = 1

    @classmethod
    def has_value(cls, value):
        return any(value == item for item in cls)


class MemoryWrapper(object):

    """
    Abstract class for DctionaryWrapper and RedisWrapper.
    """

    def __init__(self, **kwargs):
        self._mem = None
        self._mem_ready = False
        self._config = kwargs

    def setup(self):
        self._mem_ready = self._set_memory()
        return self._mem_ready

    @property
    def mem_ready(self):
        return self._mem_ready

    @abc.abstractmethod
    def _set_memory(self):
        return True

    @abc.abstractmethod
    def close(self):
        self._mem = None

    @abc.abstractmethod
    def set(self, key, value):
        return True

    @abc.abstractmethod
    def get_json_str(self, key):
        return ""

    @abc.abstractmethod
    def get(self, key):
        return None

    @abc.abstractmethod
    def delete(self, key):
        return True

    @abc.abstractmethod
    def has(self, key):
        return None

    @abc.abstractmethod
    def save(self):
        return True

    @staticmethod
    def transform_value_to_json(value):
        data = Data(value)
        data_json = json.dumps(data.r_data)
        return data_json

    @staticmethod
    def transform_json_to_value(data_json):
        data_dict = json.loads(data_json)
        data = Data()
        data.load(data_dict)
        return data.value


class Dictionary(object):

    """
    Dictionary as shared memory in a process.
    """

    __SHARED_MEMORY = {}

    def __init__(self):
        self._dict = Dictionary.__SHARED_MEMORY

    def set(self, key, value):
        self._dict[key] = value
        return True

    def get(self, key):
        if key in self._dict:
            return self._dict[key]
        else:
            return None

    def keys(self):
        return self._dict.keys()

    def delete(self, key):
        del self._dict[key]

    def exists(self, key):
        return key in self._dict


class DictionaryWrapper(MemoryWrapper):

    """
    Dictionary class wrapper class. This is used for using Dictionary as a memory.
    """

    def setup(self):
        return super(DictionaryWrapper, self).setup()

    def _set_memory(self):
        self._mem = Dictionary()
        return True

    def close(self):
        self._mem = None

    def set(self, key, value):
        data = MemoryWrapper.transform_value_to_json(value)
        self._mem.set(key, data)
        return True

    def get_json_str(self, key):
        return self._mem.get(key)

    def get(self, key):
        data = self.get_json_str(key)
        if data:
            value = MemoryWrapper.transform_json_to_value(data)
        else:
            value = None
        return value

    def delete(self, key):
        if key in self._mem.keys():
            self._mem.delete(key)
        else:
            return False
        return True

    def has(self, key):
        return self._mem.exists(key)

    def save(self):
        # TODO: save dictionary contents as a json file.
        return True


class RedisWrapper(MemoryWrapper):

    """
    Redis wrapper class. This is used for using Redis as a memory.

    :param host: Redis db host address. default: 'localhost'
    :type host: string (IP address)
    :param port: Redis db port number. default: 6379
    :type port: integer (0 ~ 65535)
    :param flush: Option to determine whether flush redis db or not after closing this wrapper object. If you set
                  flush=True, only the db which is numbered by db_num is flushed. default: True
    :type flush: boolean
    :param timeout: Timeout for db connection. It would be dangerous if you set timeout as None because the connection
                    attempt between redis client and server can block the whole process.
    :type timeout: float
    :param **kwargs: You can set extra Redis parameters by kwargs.
                    (e.g. socket_keepalive, socket_keepalive_options, connection_pool, encoding, charset and etc.)

    :returns: RedisWrapper object
    :rtype: gblackboard.wrapper.RedisWrapper
    """

    def __init__(self, host='localhost', port=6379, db_num=0, flush=True, timeout=1.0, **kwargs):
        super(RedisWrapper, self).__init__(**kwargs)
        self._host = host
        self._port = port
        self._db_num = db_num
        self._flush = flush
        self._timeout = timeout

    def setup(self):
        return super(RedisWrapper, self).setup()

    def _set_memory(self):
        if DEV_MODE:
            import fakeredis
            self._mem = fakeredis.FakeStrictRedis()
        else:
            self._mem = redis.Redis(
                host=self._host, port=self._port, db=self._db_num,
                socket_timeout=self._timeout, **self._config)
        self._validate_config()
        connected = self.connected()
        if not connected:
            self._mem = None
        return connected

    def _validate_config(self):
        # TODO: check that followings have valid values
        #       host: valid ip address value (use socket module),
        #       port: valid integer number (0~65535),
        #       db_num: > 0,
        #       timeout: > 0
        #       RedisWrongConfig can be raised.
        pass

    def connected(self):
        if not self._mem:
            return False
        return self._ping()

    def _ping(self):
        try:
            self._mem.ping()
        except redis.RedisError:
            return False
        else:
            return True

    def close(self):
        if self.connected() and self._flush:
            self._mem.flushdb()

    def set(self, key, value):
        if self._mem_ready:
            data = MemoryWrapper.transform_value_to_json(value)
            try:
                success = self._mem.set(key, data)
            except redis.ConnectionError:
                raise RedisNotConnected
        else:
            raise RedisNotConnected
        return success

    def get_json_str(self, key):
        try:
            data = self._mem.get(key)
            if data:
                data = data.decode('utf-8')
        except redis.ConnectionError:
            raise RedisNotConnected
        return data

    def get(self, key):
        if self._mem_ready:
            data = self.get_json_str(key)
            if data:
                value = MemoryWrapper.transform_json_to_value(data)
            else:
                value = None
        else:
            raise RedisNotConnected
        return value

    def delete(self, key):
        if self._mem_ready:
            try:
                result = self._mem.delete(key)
            except redis.ConnectionError:
                raise RedisNotConnected
            if result > 0:
                success = True
            else:
                success = False
        else:
            raise RedisNotConnected
        return success

    def has(self, key):
        if self._mem_ready:
            try:
                result = self._mem.exists(key)
            except redis.ConnectionError:
                raise RedisNotConnected
            if result > 0:
                existing = True
            else:
                existing = False
        else:
            raise RedisNotConnected
        return existing

    def save(self):
        # TODO: call redis.save()
        return True
