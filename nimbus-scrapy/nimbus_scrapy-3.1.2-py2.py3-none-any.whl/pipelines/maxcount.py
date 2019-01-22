# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from scrapy import signals
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.exceptions import NotConfigured, IgnoreRequest, CloseSpider


class MaxCountPipeline(object):

    def __init__(self, max_count=0, settings=None):
        if max_count <= 0:
            raise NotConfigured
        self.max_count = max_count
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        max_count = s.getint('MAX_ITEM_COUNT', 0)
        o = cls(max_count, s)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.count = 0

    def spider_closed(self, spider, reason):
        self.count = 0

    def process_item(self, item, spider, **kwargs):
        self.count += 1
        if self.count > self.max_count > 0:
            raise CloseSpider("COUNT:{} MAXCOUNT:{}".format(self.count, self.max_count))
        return item


