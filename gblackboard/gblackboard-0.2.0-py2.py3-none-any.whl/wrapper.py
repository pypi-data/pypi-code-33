# -*- coding: utf-8 -*-

import abc
import enum
import pickle
import redis
# import socket

from .data import reconstruct, load
from .exception import *


DEV_MODE = False
GBLACKBOARD = 'gblackboard'


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
        self._config = kwargs
        self.setup()

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def close(self):
        self._mem = None

    @abc.abstractmethod
    def set(self, key, value):
        return True

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
    def _get_all(self):
        """
        :return: Whole (serialized) data in blackboard
        :rtype: dict
        """
        return dict()

    @abc.abstractmethod
    def _restore(self, kv_pairs):
        """
        :param kv_pairs: (serialized) key-value pairs
        :type: dict
        :return: True if succeed to store kv_pairs to memory else False
        :rtype: bool
        """
        return True

    @staticmethod
    def transform_value_to_pickle(value):
        return reconstruct(value)

    @staticmethod
    def transform_pickle_to_value(data):
        return load(data)

    def save(self, file_path):
        whole_data = self._get_all()
        with open(file_path, 'wb') as outfile:
            pickle.dump(whole_data, outfile, protocol=pickle.HIGHEST_PROTOCOL)
        return True

    def load(self, file_path):
        with open(file_path, 'rb') as infile:
            read_data = pickle.load(infile)
        if type(read_data) is not dict:
            raise ReadWrongFile("File contents must be dictionary data: {}".format(read_data))
        self._restore(read_data)
        return True


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

    def flush(self):
        self._dict.clear()

    @property
    def all(self):
        return self._dict


class DictionaryWrapper(MemoryWrapper):

    """
    Dictionary class wrapper class. This is used for using Dictionary as a memory.
    """

    def setup(self):
        self._mem = Dictionary()

    def close(self):
        self._mem.flush()

    def set(self, key, value):
        data = MemoryWrapper.transform_value_to_pickle(value)
        self._mem.set(key, data)
        return True

    def get(self, key):
        data = self._mem.get(key)
        if data:
            value = MemoryWrapper.transform_pickle_to_value(data)
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

    def _get_all(self):
        """
        :return: Whole (serialized) data in blackboard
        :rtype: dict
        """
        return self._mem.all

    def _restore(self, kv_pairs):
        """
        :param kv_pairs: (serialized) key-value pairs
        :type: dict
        :return: True if succeed to store kv_pairs to memory else False
        :rtype: bool
        """
        self._mem.flush()
        for key, val in kv_pairs.items():
            if type(key) is bytes:
                key = key.decode("utf-8")
            self._mem.set(key, val)
        return True


def raise_conn_error(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except redis.ConnectionError:
            raise RedisNotConnected
        return result
    return wrapper


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
        self._host = host
        self._port = port
        self._db_num = db_num
        self._flush = flush
        self._timeout = timeout
        super(RedisWrapper, self).__init__(**kwargs)

    def setup(self):
        if DEV_MODE:
            import fakeredis
            self._mem = fakeredis.FakeStrictRedis()
        else:
            self._mem = redis.Redis(
                host=self._host, port=self._port, db=self._db_num,
                socket_timeout=self._timeout, **self._config)
        self._validate_config()

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

    def _flush_hash(self):
        keys = self._mem.hkeys(GBLACKBOARD)
        if keys:
            self._mem.hdel(GBLACKBOARD, *keys)

    @raise_conn_error
    def close(self):
        if self._flush:
            self._flush_hash()

    @raise_conn_error
    def set(self, key, value):
        data = MemoryWrapper.transform_value_to_pickle(value)
        try:
            self._mem.hset(GBLACKBOARD, key, data)
        except redis.exceptions.DataError:
            return False
        return True

    @raise_conn_error
    def get(self, key):
        data = self._mem.hget(GBLACKBOARD, key)
        if data:
            return MemoryWrapper.transform_pickle_to_value(data)
        else:
            return None

    @raise_conn_error
    def delete(self, key):
        result = self._mem.hdel(GBLACKBOARD, key)
        if result > 0:
            return True
        else:
            return False

    @raise_conn_error
    def has(self, key):
        result = self._mem.hexists(GBLACKBOARD, key)
        if result > 0:
            return True
        else:
            return False

    @raise_conn_error
    def _get_all(self):
        """
        :return: Whole (serialized) data in blackboard
        :rtype: dict
        """
        return self._mem.hgetall(GBLACKBOARD)

    @raise_conn_error
    def _restore(self, kv_pairs):
        """
        :param kv_pairs: (serialized) key-value pairs
        :type: dict
        :return: True if succeed to store kv_pairs to memory else False
        :rtype: bool
        """
        self._flush_hash()
        for key, val in kv_pairs.items():
            self._mem.hset(GBLACKBOARD, key, val)
        return True

