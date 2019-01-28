# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from twisted.internet import reactor, defer
from scrapy.resolver import CachingThreadedResolver
from scrapy.crawler import CrawlerProcess as ScrapyCrawlerProcess
from scrapy.crawler import CrawlerRunner as ScrapyCrawlerRunner
from scrapy.utils.log import (
    LogCounterHandler, configure_logging, log_scrapy_info,
    get_scrapy_root_handler, install_scrapy_root_handler
)

__all__ = [
    "CrawlerProcess",
    "CrawlerRunner",
]


class CrawlerProcess(ScrapyCrawlerRunner):

    def __init__(self, settings=None, install_root_handler=True):
        super(CrawlerProcess, self).__init__(settings)
        configure_logging(self.settings, install_root_handler)
        log_scrapy_info(self.settings)

    def start(self, stop_after_crawl=True):
        pass


class CrawlerRunner(ScrapyCrawlerRunner):

    def __init__(self, settings=None, install_root_handler=True):
        super(CrawlerRunner, self).__init__(settings)

    def start(self, stop_after_crawl=True):
        pass
