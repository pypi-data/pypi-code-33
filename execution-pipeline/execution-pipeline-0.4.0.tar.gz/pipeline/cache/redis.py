import pickle
import logging

logger = logging.getLogger(__name__)


try:
    from redis import Redis
except ImportError as e:
    logger.warning('Could not import from redis, using MockCache object instead.')
    from . mock import MockCache as Redis


class RedisCache(Redis):

    def __init__(self, host='localhost', port=6379, **kwargs):
        super().__init__(host=host, port=port, **kwargs)

    def get(self, key=None, default=None):
        cached_pickle = super().get(key)
        cached_obj = pickle.loads(cached_pickle) if cached_pickle else default
        return cached_obj

    def set(self, key=None, obj=None, expiration_seconds=3600):
        if key is None or obj is None:
            logging.warning('object was not cached.')
            return False
        else:
            pickled_obj = pickle.dumps(obj)
            super().set(key, pickled_obj, expiration_seconds)
        return True

    def clear(self):
        self.flushdb()
