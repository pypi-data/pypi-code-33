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

    def __init__(self, enabled=False, reset=False, flush=False, expire=0, prefix="delta", config=None, stats=None):
        if not enabled:
            raise NotConfigured
        self.enabled = enabled
        self.reset = reset
        self.flush = flush
        self.expire = expire
        self.config = config or {}
        self.stats = stats
        self.redis = None
        self.prefix = prefix

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        enabled = s.getbool('DELTAFETCH_ENABLED', False)
        reset = s.getbool('DELTAFETCH_RESET', False)
        flush = s.getbool('DELTAFETCH_FLUSH', False)
        expire = s.getint('DELTAFETCH_EXPIRE', 0)
        prefix = s.getint('DELTAFETCH_PREFIX', "delta")
        config = s.get('DELTAFETCH_REDIS', {})
        o = cls(enabled=enabled, reset=reset, flush=flush, expire=expire, prefix=prefix, config=config, stats=crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        try:
            self.redis = redis.StrictRedis(**self.config)
            self.redis.ping()
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
