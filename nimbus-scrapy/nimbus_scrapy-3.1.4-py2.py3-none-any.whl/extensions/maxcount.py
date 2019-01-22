# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from collections import defaultdict
from scrapy import signals
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.exceptions import NotConfigured, IgnoreRequest, CloseSpider


class MaxCount(object):

    def __init__(self, crawler):
        self.crawler = crawler
        max_count = crawler.settings.getint('MAX_ITEM_COUNT', 0)
        if max_count <= 0:
            raise NotConfigured
        self.max_count = max_count
        self.counter = defaultdict(int)
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def item_scraped(self, item, spider):
        self.counter['itemcount'] += 1
        if self.counter['itemcount'] >= self.max_count:
            self.crawler.engine.close_spider(spider, 'max_item_count')

    def spider_closed(self, spider):
        task = getattr(self, 'task', False)
        if task and task.active():
            task.cancel()


