# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import sys
import logging
import json
import time
import redis
from redis.exceptions import RedisError
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.utils.misc import arg_to_iter
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy import signals
from nimbus_utils.urlparse import urlsplit, urlparse
from nimbus_utils.encoding import smart_text
from ..item import DeltaFetchItem, Item
logger = logging.getLogger(__name__)


class DeltaFetch(object):
    """
    This is a spider middleware to ignore requests to pages containing items
    seen in previous crawls of the same spider, thus producing a "delta crawl"
    containing only new items.

    This also speeds up the crawl, by reducing the number of requests that need
    to be crawled, and processed (typically, item requests are the most cpu
    intensive).

    finger_fields = ['scheme', 'netloc', 'path', 'query', 'fragment']
    """

    def __init__(self, crawler=None):
        s = crawler.settings
        _stats = crawler.stats
        _enabled = s.getbool('DELTAFETCH_ENABLED', False)
        _reset = s.getbool('DELTAFETCH_RESET', False)
        _flush = s.getbool('DELTAFETCH_FLUSH', False)
        _expire = s.getint('DELTAFETCH_EXPIRE', 0)
        _prefix = s.get('DELTAFETCH_PREFIX', "delta")
        _config = s.getdict('DELTAFETCH_REDIS', {})
        _finger_fields = s.get("DELTAFETCH_FINGER_FIELDS", [])
        _redis = self._check_redis(_config)

        if not (_enabled and _redis):
            raise NotConfigured
        self.enabled = _enabled
        self.reset = _reset
        self.flush = _flush
        self.expire = _expire
        self.prefix = _prefix
        self.redis = _redis
        self.stats = _stats
        self.finger_fields = _finger_fields

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler=crawler)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def _check_redis(self, config):
        try:
            _redis = redis.StrictRedis(**config)
            _redis.ping()
            return _redis
        except Exception as e:
            return None

    def spider_opened(self, spider):
        try:
            if self.flush:
                self.redis.flushdb()
            if self.reset:
                key = "{}-*".format(self.prefix)
                keys = self.redis.keys(key)
                for k in keys:
                    self.redis.delete(k)
        except Exception as e:
            self.enabled = False

    def spider_closed(self, spider):
        self.redis = None

    def process_spider_output(self, response, result, spider):
        def _filter(r, enabled=False):
            if not enabled:
                return True
            else:
                if isinstance(r, Request):
                    key = self._get_key(r)
                    if key is not None and self._exists(key=key):
                        if self.stats:
                            self.stats.inc_value('deltafetch/skipped', spider=spider)
                        return False
                elif isinstance(r, (BaseItem, dict)):
                    key = self._get_key(response.request, r)
                    if key is not None:
                        expire = self._get_expire(response.request)
                        value = "{}".format(time.time())
                        self._set_key(key=key, value=value)
                        self._set_expire(key=key, expire=expire)
                        if self.stats:
                            self.stats.inc_value('deltafetch/stored', spider=spider)
                return True
        return [r for r in result or [] if _filter(r, self.enabled)]

    def _get_key(self, request, item=None):
        key = request.meta.get('deltafetch_key', None) or self._get_item_id(item)
        if key is None:
            return key
        key = key or self._get_fingerprint(request) or request_fingerprint(request)
        return "{}-{}".format(self.prefix, smart_text(key))

    def _get_expire(self, request):
        expire = request.meta.get('deltafetch_expire', 0)
        return expire

    def _get_item_id(self, item):
        if item and isinstance(item, Item):
            return item.get("deltafetch_key", None)
        return None

    def _get_fingerprint(self, request):
        if self.finger_fields:
            parsed = urlsplit(request.url)
            finger = "".join(["".format(getattr(parsed, f, "")) for f in self.finger_fields])
        else:
            finger = ""
        return finger

    def _exists(self, key):
        return self.redis.exists(key)

    def _set_key(self, key, value):
        self.redis.set(key, value)

    def _set_expire(self, key, expire=0):
        expire = expire if expire else self.expire
        if expire > 0:
            self.redis.expire(key, expire)
