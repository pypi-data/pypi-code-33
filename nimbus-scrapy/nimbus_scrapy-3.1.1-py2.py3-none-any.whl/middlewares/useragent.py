# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.exceptions import NotConfigured, IgnoreRequest


class RandomUserAgentMiddleware(object):

    def __init__(self, settings=None):
        try:
            enabled = settings.get('RANDOM_UA_ENABLED', False)
            if not enabled:
                raise NotConfigured
            from fake_useragent import UserAgent
            self.ua = UserAgent()
            self.ua_type = settings.get('RANDOM_UA_TYPE', 'random')
            self.enabled = enabled
        except Exception as e:
            raise NotConfigured

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings)
        return o

    def process_request(self, request, spider):
        if not self.enabled:
            return
        ua = getattr(self.ua, self.ua_type, None)
        if ua:
            request.headers.setdefault('User-Agent', ua)


