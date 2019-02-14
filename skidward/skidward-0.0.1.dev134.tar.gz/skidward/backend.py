from functools import partialmethod
import logging
import os

from redis import StrictRedis

logger = logging.getLogger(__name__)


class RedisProxy:
    def __init__(self, backend):
        self.backend = backend

    def proxy(self, method, *args, **kwargs):
        errors = {}

        backend_name = self.backend.__class__.__name__
        try:
            logger.debug(
                "trying to {} {} using {}".format(method, kwargs, backend_name)
            )
            bound_method = getattr(self.backend, method)
            return bound_method(*args, **kwargs)
        except Exception as e:
            if os.getenv("DEBUG"):
                raise
            errors[backend_name] = str(e)

        raise Exception(
            "no backend managed to {} for the provided request: {}".format(
                method, errors
            )
        )

    lpush = partialmethod(proxy, "lpush")
    lrange = partialmethod(proxy, "lrange")
    erase = partialmethod(proxy, "erase")


class RedisDummyBackend:
    def __init__(self, **kwargs):
        self.redis_lists = {}

    def job_exists(self, name):
        return name in self.redis_lists

    def lpush(self, name, elements):
        if not isinstance(elements, list):
            elements = [elements]

        elements = [str(element).encode("utf-8") for element in elements]

        if not name in self.redis_lists:
            self.redis_lists[name] = []

        self.redis_lists[name] = elements + self.redis_lists[name]

    def lrange(self, name, start, end):
        if not self.job_exists(name):
            self.redis_lists[name] = []

        if end == -1:
            return self.redis_lists[name][start:]
        else:
            end = end + 1

        result = self.redis_lists[name][start:end]

        return result

    def erase(self):
        self.redis_lists = {}


def RedisBackend(**kwargs):
    testing = os.getenv("TESTING") or not os.getenv("REDIS_BACKEND")
    if testing:
        flavors = ("dummy",)
    else:
        flavors = (os.getenv("REDIS_BACKEND"),)

    for flavor in flavors:
        backend = {"dummy": RedisDummyBackend, "redis": StrictRedis}[flavor](**kwargs)

    redis_client = RedisProxy(backend)

    return redis_client
