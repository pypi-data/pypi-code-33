from redis import StrictRedis

from .base import ConfigStoreBase, ConfigurationNotFound


class RedisStore(ConfigStoreBase):
    __slots__ = ["redis"]

    def __init__(self, redis: StrictRedis):
        """Initialize the Redis configuration store

        :param redis: Handle to the Redis connection to use to retrieve
                      configuration from
        :type redis: StrictRedis
        """

        self.redis = redis

    def retrieve(self, name: str) -> str:
        """Retrieve configuration from Redis

        :param name: Name of the configuration to retrieve
        :param name: str
        :raises ConfigurationNotFound: if the named configuration can't be found
        :return: The configuration "file" contents
        :rtype: str
        """

        super().retrieve(name)

        with self.statsd.get_timer().time("retrieve_time"):
            config = self.redis.get("saas:instance:" + name)

        self.statsd.get_counter().increment("retrieve")

        if not config:
            self.statsd.get_counter().increment("retrieve_miss")
            raise ConfigurationNotFound

        return config.decode("utf-8")
