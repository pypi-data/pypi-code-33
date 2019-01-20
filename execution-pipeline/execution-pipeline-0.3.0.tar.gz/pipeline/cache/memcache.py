import pickle
import logging

logger = logging.getLogger(__name__)

try:
    from memcache import Client
except ImportError as e:
    logger.warning('Could not import from memcache, using MockCache object instead.')
    from . mock import MockCache as Client


class MemCache(Client):

    def __init__(self, host='localhost', port=11211, **kwargs):
        """

        :param args: (host, port)
        """
        args = (host, int(port))
        super().__init__([
            args
        ], **kwargs)

    def get(self, key=None, default=None):
        # memcached requires binary string
        byte_key = str(key).encode('ascii')
        cached_pickle = super().get(byte_key)
        cached_obj = pickle.loads(cached_pickle) if cached_pickle else default
        return cached_obj

    def set(self, key=None, obj=None, expiration_seconds=3600):
        if key is None or obj is None:
            logging.warning('object was not cached.')
            return False
        else:
            # memcached requires binary string
            byte_key = str(key).encode('ascii')
            pickled_obj = pickle.dumps(obj)
            super().set(byte_key, pickled_obj, expiration_seconds)
        return True

    def clear(self):
        self.flushdb()
