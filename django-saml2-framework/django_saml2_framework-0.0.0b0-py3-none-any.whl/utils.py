import collections

from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError


def deepmerge(dct, merge_dct):
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            deepmerge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def get_cache_store(cache_name='saml2'):
    try:
        return caches[cache_name]
    except InvalidCacheBackendError:
        pass
    return caches['default']


class DjangoCacheDict(object):
    
    def init(self, cache=None, cache_name='saml2', prefix=None):
        if not prefix:
            raise ValueError('you need a prefix')

        self.prefix = prefix  # todo: must be a string
        self.cache = cache  # todo: must be a django cache thing
    
    def get_cache_store(self, cache_name):
        if cache_name in caches:
            return caches[cache_name]
        return caches['default']

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        return self.cache.set(key, value)

