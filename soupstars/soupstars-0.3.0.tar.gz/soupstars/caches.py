"""
Caches
------

Caches help reduce unnecessary loading requests. The `DefaultCache` is just a
a python dictionary with some additional features.

>>> from soupstars import DefaultCache
>>> cache = DefaultCache()
>>> cache.set('key', 'value')
>>> cache.get('key')
'value'

Unlike dictionary, caches provide a hashing function that transforms a `Loader`
along with its `load` keyword arguments into a unique string. This
allows the cache to uniquely identify a `Loader`'s response without
actually calling the `load` method of the `Loader`.

>>> from soupstars import DefaultLoader
>>> loader = DefaultLoader()
>>> id = cache.hash_id(loader, a=1, b=2)
>>> id
'ac6dcde3d009f3b5d2ea803c12ef1a3c'

Caches also allow updating a key using a `Loader` instance directly.

>>> cache.update('key', loader, a=1, b=2)
{'a': 1, 'b': 2}
>>> cache.get('key')
{'a': 1, 'b': 2}

For a more persistent cache, you can use the `FilesystemCache` to store
responses forever. If you need a cache available to multiple nodes, you can
use the RedisCache, which stores `load` responses for a single day.
"""

import hashlib
import redis
import pickle
import os

from .exceptions import NotImplementedError
from .config import SoupstarsConfig
from .utils import SoupstarsPlugin


config = SoupstarsConfig()

class BaseCache(SoupstarsPlugin):
    """
    Basic cache definition. Any subclass must define get and set methods.
    """

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    # I think there might be a better hashing strategy. See this:
    # https://stackoverflow.com/questions/5884066/hashing-a-dictionary
    def hash_id(self, loader, **kwargs):
        """
        Uses the class and keyword args to generate a unique id for a
        loader. Can receive any other keyword args, such as a loader's init
        args, to make the id unique
        """

        load_args = [':'.join(str(item) for item in kwargs.items())]
        if load_args:
            load_args = '_'.join(load_args)
        else:
            load_args = ""

        name_value = str(loader.__class__)
        string_value = " | ".join([load_args, name_value])
        hash_value = hashlib.md5(string_value.encode('utf8'))
        return hash_value.hexdigest()

    def update(self, key, loader, **loader_args):
        """
        Updates the cache's `key` value using the response from calling
        `loader.load(**loader_args)`.
        """

        load = loader.load(**loader_args)
        self.set(key, load)
        return load


class DefaultCache(BaseCache):
    """
    A simple in-memory cache. Expires at the end of a python session.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value


class RedisCache(BaseCache):
    """
    A redis backed cache. Stores items for one day. Using the cache requires
    the environment variable `SOUPSTARS_REDIS_URL` set. Cached items are stored
    as python `Pickle` objects.
    """

    # TODO: use config here
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            self.URL = config['SOUPSTARS_REDIS_URL']
        except KeyError:
            msg = """Couldn't find a redis url in the environment. You need to
            set SOUPSTARS_REDIS_URL in order to use a redis backend.
            """
            raise KeyError(msg)

        self._cache = redis.Redis.from_url(self.URL)

    def get(self, key):
        pickled_value = self._cache.get(key)
        if pickled_value is None:
            return None
        return pickle.loads(pickled_value)

    def set(self, key, value):
        pickled_value = pickle.dumps(value)
        self._cache.set(key, pickled_value, ex=60*60*24)  # 1 day


class FilesystemCache(BaseCache):
    """
    A filesystem backed cache. Stores items forever.

    Using this cache will create a folder under $HOME/.soupstars. If the
    process does not have write access to $HOME, the cache will fail.
    """

    # TODO: use config here
    def __init__(self, *args, **kwargs):
        home_dir = os.path.expanduser('~')
        cache_dir = os.path.join(home_dir, 'soupstars', 'cache')
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        self.URL = cache_dir

    def get(self, key):
        filename = os.path.join(self.URL, key + '.cache')
        if not os.path.exists(filename):
            return None
        else:
            with open(filename, 'rb') as file_handle:
                return pickle.load(file_handle)

    def set(self, key, value):
        filename = os.path.join(self.URL, key + '.cache')
        with open(filename, 'wb') as file_handle:
            pickle.dump(value, file_handle)
