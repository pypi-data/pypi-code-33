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
from ..utils import smart_text
logger = logging.getLogger(__name__)


class DeltaFetch(object):
    """
    This is a spider middleware to ignore requests to pages containing items
    seen in previous crawls of the same spider, thus producing a "delta crawl"
    containing only new items.

    This also speeds up the crawl, by reducing the number of requests that need
    to be crawled, and processed (typically, item requests are the most cpu
    intensive).
    """

    def __init__(self, enabled=False, redis=None, reset=False, flush=False, expire=0, prefix="delta", stats=None):
        if not (enabled and redis):
            raise NotConfigured
        self.enabled = enabled
        self.reset = reset
        self.flush = flush
        self.expire = expire
        self.prefix = prefix
        self.redis = redis
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        _stats = crawler.stats
        _enabled = s.getbool('DELTAFETCH_ENABLED', False)
        _reset = s.getbool('DELTAFETCH_RESET', False)
        _flush = s.getbool('DELTAFETCH_FLUSH', False)
        _expire = s.getint('DELTAFETCH_EXPIRE', 0)
        _prefix = s.get('DELTAFETCH_PREFIX', "delta")
        _config = s.getdict('DELTAFETCH_REDIS', {})
        _redis = cls._check_redis(_config)
        o = cls(enabled=_enabled, redis=_redis, reset=_reset, flush=_flush, expire=_expire, prefix=_prefix, stats=_stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    @classmethod
    def _check_redis(cls, config):
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
                    if self._exists(key=key):
                        if self.stats:
                            self.stats.inc_value('deltafetch/skipped', spider=spider)
                        return False
                elif isinstance(r, (BaseItem, dict)):
                    key = self._get_key(response.request)
                    expire = self._get_expire(response.request)
                    value = "{}".format(time.time())
                    self._set_key(key=key, value=value)
                    self._set_expire(key=key, expire=expire)
                    if self.stats:
                        self.stats.inc_value('deltafetch/stored', spider=spider)
                return True
        return [r for r in result or [] if _filter(r, self.enabled)]

    def _get_key(self, request):
        key = request.meta.get('deltafetch_key') or request_fingerprint(request)
        return "{}-{}".format(self.prefix, smart_text(key))

    def _get_expire(self, request):
        expire = request.meta.get('deltafetch_expire', 0)
        return expire

    def _exists(self, key):
        return self.redis.exists(key)

    def _set_key(self, key, value):
        self.redis.set(key, value)

    def _set_expire(self, key, expire=0):
        expire = expire if expire else self.expire
        if expire > 0:
            self.redis.expire(key, expire)
