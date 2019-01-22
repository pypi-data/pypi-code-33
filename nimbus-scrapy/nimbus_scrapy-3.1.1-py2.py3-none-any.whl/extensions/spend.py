# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import sys
import time
import logging
import datetime
from datetime import timedelta
from scrapy import signals
from scrapy.exceptions import NotConfigured


class SpendStats(object):
    def __init__(self, stats):
        self.stats = stats
        self.time_st = time.time()

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('SPEND_STATS_ENABLED'):
            raise NotConfigured
        o = cls(crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider, *args, **kwargs):
        self.time_st = time.time()

    def spider_closed(self, spider, reason, *args, **kwargs):
        delta = int(time.time() - self.time_st)
        d = "{}".format(timedelta(seconds=delta))
        self.stats.set_value('spend_time', d, spider=spider)



