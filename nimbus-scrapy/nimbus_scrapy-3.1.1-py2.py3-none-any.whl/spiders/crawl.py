# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import logging
import json
from functools import wraps
from scrapy.spiders import Spider, CrawlSpider, CSVFeedSpider, SitemapSpider, XMLFeedSpider
from .mixins import BaseMixin, SeleniumMixin


class NBSpider(BaseMixin, Spider):
    pass


class NBCrawlSpider(BaseMixin, CrawlSpider):
    pass


class NBCSVFeedSpider(BaseMixin, CSVFeedSpider):
    pass


class NBSitemapSpider(BaseMixin, SitemapSpider):
    pass


class NBXMLFeedSpider(BaseMixin, XMLFeedSpider):
    pass


class NSSpider(SeleniumMixin, Spider):
    pass


class NSCrawlSpider(SeleniumMixin, CrawlSpider):
    pass


class NSCSVFeedSpider(SeleniumMixin, CSVFeedSpider):
    pass


class NSSitemapSpider(SeleniumMixin, SitemapSpider):
    pass


class NSXMLFeedSpider(SeleniumMixin, XMLFeedSpider):
    pass

