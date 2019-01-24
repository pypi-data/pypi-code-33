# -*- coding: utf-8 -*-

import dogpile.cache


__version__ = '0.0.2'


# I'm not sure how to get to this without reaching in to a private method
class CacheToolsBackend(dogpile.cache.region._backend_loader.load('dogpile.cache.memory')):
    argsKeys = ()
    kwargsKeys = ()

    def __init__(self, arguments):
        self._imports()
        args = (arguments.pop(key, None) for key in self.argsKeys)
        kwargs = {key: arguments.pop(key, None) for key in self.kwargsKeys if key in arguments}
        arguments['cache_dict'] = getattr(cachetools, self.cachetoolsClass)(*args, **kwargs)
        super(CacheToolsBackend, self).__init__(arguments)

    def _imports(self):
        # defer imports until backend is used
        global cachetools
        import cachetools  # noqa


class LFUMemoryBackend(CacheToolsBackend):
    argsKeys = ('maxsize', )
    kwargsKeys = ('getsizeof', )
    cachetoolsClass = 'LFUCache'


class LRUMemoryBackend(CacheToolsBackend):
    argsKeys = ('maxsize', )
    kwargsKeys = ('getsizeof', )
    cachetoolsClass = 'LRUCache'


class RRMemoryBackend(CacheToolsBackend):
    argsKeys = ('maxsize', )
    kwargsKeys = ('choice', 'getsizeof')
    cachetoolsClass = 'RRCache'


class TTLMemoryBackend(CacheToolsBackend):
    argsKeys = ('maxsize', 'ttl')
    kwargsKeys = ('timer', 'getsizeof', )
    cachetoolsClass = 'TTLCache'


dogpile.cache.register_backend(
    "dogpile.cache.cachetools_lfu", "dogpile_cache_cachetools",
    "LFUMemoryBackend")
dogpile.cache.register_backend(
    "dogpile.cache.cachetools_lru", "dogpile_cache_cachetools",
    "LRUMemoryBackend")
dogpile.cache.register_backend(
    "dogpile.cache.cachetools_rr", "dogpile_cache_cachetools",
    "RRMemoryBackend")
dogpile.cache.register_backend(
    "dogpile.cache.cachetools_ttl", "dogpile_cache_cachetools",
    "TTLMemoryBackend")
