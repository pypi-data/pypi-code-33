# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

class DingTalkCacheItem(object):
    _name = None
    _DEFAULT_TTL = 60*60*2-100

    def __init__(self, cache=None, prefix=None, name=None):
        self.cache = cache
        self.prefix = prefix
        if name is None:
            self.name = self._name
        else:
            self.name = name

    def key_name(self, key):
        if isinstance(key, (tuple, list)):
            key = ':'.join(key)

        k = '{0}:{1}'.format(self.prefix, self.name)
        if key is not None:
            k = '{0}:{1}'.format(k, key)
        return k

    def get(self, key=None):
        return self.cache.get(self.key_name(key))

    def set(self, key=None, value=None, ttl=_DEFAULT_TTL):
        return self.cache.set(self.key_name(key), value, ttl)

    def delete(self, key=None):
        return self.cache.delete(self.key_name(key))


class DingTalkAccessTokenItem(DingTalkCacheItem):
    _name = 'access_token'


class DingTalkJsapiTicketItem(DingTalkCacheItem):
    _name = 'jsapi_ticket'

def _is_cache_item(obj):
    return isinstance(obj, DingTalkCacheItem)

class DingTalkCache(object):
    access_token = None
    jsapi_ticket = None

    def __init__(self, storage, prefix='client'):
        self.storage = storage
        self.prefix = prefix
        # TODO 
        self.access_token = DingTalkAccessTokenItem(self.storage, prefix)
        self.jsapi_ticket = DingTalkJsapiTicketItem(self.storage, prefix)
