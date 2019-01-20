import logging
import pickle
import time

logger = logging.getLogger(__name__)


class MockCache:

    def __init__(self, debug=False, **kwargs):
        self.debug = True if debug else False
        self.store = dict()

    def get(self, key=None, default=None):
        stored = self.store.get(key, default)
        if stored is not None:
            expiration = stored.get('expiration', None)
            if expiration is not None and expiration > time.time():
                pickled_obj = pickle.loads(stored.get('pickled_obj'))
                return pickled_obj

    def set(self, key=None, obj=None, expiration_seconds=3600):
        if key is None or obj is None:
            logging.warning('object was not cached.')
            return False
        else:
            self.store[key] = {'pickled_obj': pickle.dumps(obj), 'expiration': time.time() + expiration_seconds}
        return True

    def clear(self):
        self.flushdb()

    def flushdb(self):
        self.store = dict()
