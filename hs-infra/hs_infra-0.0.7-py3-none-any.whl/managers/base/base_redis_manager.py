import redis

from hs_infra.managers.base.base_manager import BaseManager


class BaseRedisManager(BaseManager):
    HOST_IP = 'localhost'
    HOST_PORT = 6379
    DB = 0
    MAX_CONNECTIONS = None
    DECODE_RESPONSES = None
    PASSWORD = None

    def __init__(self, *args, **params):
        super().__init__(*args, **params)
        if self.HOST_IP is not None:
            params['host'] = self.HOST_IP
        if self.HOST_PORT is not None:
            params['port'] = self.HOST_PORT
        if self.DB is not None:
            params['db'] = self.DB
        if self.MAX_CONNECTIONS is not None:
            params['max_connections'] = self.MAX_CONNECTIONS
        if self.DECODE_RESPONSES is not None:
            params['decode_responses'] = self.DECODE_RESPONSES
        if self.PASSWORD is not None:
            params['password'] = self.PASSWORD

        self.pool = redis.ConnectionPool(**params)

    def get_connection(self, *args, **kwargs):
        kwargs["connection_pool"] = self.pool

        return redis.Redis(*args, **kwargs)

    def set(self, key, value, ex=None):
        return self.get_connection().set(key, value, ex)

    def get(self, key, default=None):
        result = self.get_connection().get(key)
        if result is None:
            result = default
        return result
