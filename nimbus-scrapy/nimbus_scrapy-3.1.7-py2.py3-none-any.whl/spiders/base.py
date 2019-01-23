# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
"""
Package Description

Configuration
=================================================================================
{
    "id": "user spider's id",
    "name": "user spider's name",
    "sid": "spider's id",
    "sname": "spider's name",
    "db": {
        "db_uri": "{dialect}{user}:{password}@{host}:{port}/{db}",
        "dialect": "postgresql://",
        "host": "xxx.xxx.xxx.xxx",
        "port": "5432",
        "db": "xxx",
        "user": "xxx",
        "password": "xxx"
    },
    "redis": {
        "host": '127.0.0.1',
        "port": 6379,
        "db": 0,
        "password": None
    },
    "proxy": [
        ["http", "http://39.137.83.130:8080"],
    ],
    "spider": {
        "max_pages": 2,
        "clean_urls": [[uid, url], ],
        "date": {
            "period": "days",
            "every": 5,
        },
        "keywords": ["KEY1", "KEY2", ]
    }
}

"""
import os
import sys
import six
import json
import logging
import datetime
import time
import random
import platform
import hashlib
import uuid
import copy
import traceback
from collections import OrderedDict
from w3lib.html import remove_tags
from bs4 import BeautifulSoup
import scrapy
from scrapy import signals
from scrapy.spiders import Spider, CrawlSpider, CSVFeedSpider, SitemapSpider, XMLFeedSpider
from scrapy.spiders import Rule
from scrapy.http import Request
from scrapy.http import Response
from scrapy.http.request.form import FormRequest
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.xml import XmlResponse
from scrapy.http.response.text import TextResponse
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.exceptions import DropItem
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException
from .mixin import BaseMixin
from .. import utils

UA_FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"
UA_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7"
UA_PHANTOMJS = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1"


class AbstractSpider(BaseMixin, Spider):
    name = None
    allowed_domains = []
    start_urls = []

    spider_args = []
    spider_kwargs = {}
    DEFAULT_UA = UA_FIREFOX
    TIME_TO_WAIT = 30

    _driver = None
    _proxy = None

    def start_requests(self):
        return super(AbstractSpider, self).start_requests()

    def parse(self, response):
        raise NotImplementedError

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        cls.spider_args = copy.deepcopy(args)
        cls.spider_kwargs = copy.deepcopy(kwargs)
        config = kwargs.pop("config", None)
        spider = super(AbstractSpider, cls).from_crawler(crawler, *args, **kwargs)
        try:
            spider.log(message="name: {}".format(spider.name), level=logging.INFO)
            spider.log(message="args: {}".format(spider.spider_args), level=logging.INFO)
            spider.log(message="kwargs: {}".format(spider.spider_kwargs), level=logging.INFO)
            if config is None:
                spider.log(message="config is None", level=logging.ERROR)
            else:
                spider.log(message=config, level=logging.DEBUG)
                spider.auto_setup(config)
                spider.log("CONFIG sid:[{sid}] sname:[{sname}] version: [{version}]".format(sid=spider.sid, sname=spider.sname, version=spider.version), level=logging.INFO)
                spider.log("CONFIG spider_id:[{spider_id}] spider_name:[{spider_name}]".format(spider_id=spider.spider_id, spider_name=spider.spider_name), level=logging.INFO)
                spider.log("CONFIG config: {config}".format(config=json.dumps(spider.config, ensure_ascii=False, indent=2)), level=logging.INFO)
                spider.log("SPIDER spider_config: {config}".format(config=json.dumps(spider.spider_config, ensure_ascii=False, indent=2)), level=logging.INFO)
        except ValueError as e:
            spider.log(e, level=logging.ERROR)
            raise e
        except Exception as e:
            spider.log(e, level=logging.ERROR)
            traceback.print_exc()
        return spider

    @staticmethod
    def close(spider, reason, **kwargs):
        if isinstance(spider, AbstractSpider):
            spider._close_browser()
        return super(AbstractSpider, spider).close(spider, reason)

    def _get_capabilities(self, capabilities=None, proxy=None):
        if proxy:
            result = utils.urlparse(proxy)
            scheme = result.scheme
            netloc = result.netloc
            webproxy = webdriver.Proxy()
            webproxy.proxy_type = ProxyType.MANUAL
            if scheme == "http":
                webproxy.http_proxy = netloc
            elif scheme == "https":
                webproxy.sslProxy = netloc
            webproxy.add_to_capabilities(capabilities)
        return capabilities

    def _get_webdriver(self, proxy=None, **kwargs):
        userAgent = kwargs.pop("userAgent", self.DEFAULT_UA)
        system = platform.system()
        capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        capabilities["phantomjs.page.settings.userAgent"] = userAgent
        capabilities["phantomjs.page.customHeaders.User-Agent"] = userAgent
        capabilities = self._get_capabilities(capabilities=capabilities, proxy=proxy)
        driver = webdriver.PhantomJS(desired_capabilities=capabilities, **kwargs)
        driver.maximize_window()
        driver.implicitly_wait(self.TIME_TO_WAIT)
        driver.set_script_timeout(self.TIME_TO_WAIT)
        driver.set_page_load_timeout(self.TIME_TO_WAIT)
        return driver, proxy

    def _close_browser(self):
        try:
            if self._driver:
                self._driver.quit()
            self._driver = None
            self._proxy = None
        except Exception as e:
            self.log(e, level=logging.ERROR)
            self._driver = None
            self._proxy = None

    def get_browser(self, proxy=None, **kwargs):
        try:
            if self._driver and self._proxy == proxy:
                return self._driver
            if self._driver:
                self._close_browser()
            self._driver, self._proxy = self._get_webdriver(proxy=proxy, **kwargs)
        except SessionNotCreatedException as e:
            self.log(e, level=logging.ERROR)
            self._close_browser()
            time.sleep(2)
            self._driver, self._proxy = self._get_webdriver(proxy=proxy, **kwargs)
        return self._driver

    def get_kwargs(self, key, default=None):
        value = self.spider_kwargs.get(key, None)
        if value is None and hasattr(self, key):
            value = getattr(self, key, default)
        return value or default

    def get_base_url(self, response):
        return get_base_url(response=response)

    def get_queryparam(self, query=None):
        try:
            return utils.parse_qs(query)
        except Exception as e:
            self.log(e, level=logging.ERROR)
            return {}

    def set_crawled(self, req, key):
        if not all([req, key]):
            raise ValueError("req and key not empty.")
        if isinstance(req, Request):
            request = req
            request.meta.update({'deltafetch_key': utils.md5(key)})
        elif isinstance(req, Response):
            request = req.request
            request.meta.update({'deltafetch_key': utils.md5(key)})

    def get_url_id(self, url=None):
        if self.spider_id and url:
            return "{}_{}".format(self.spider_id, utils.md5(url))
        return None

    def extract_xpath(self, sel, xpath, index=0, default=""):
        datas = sel.xpath(xpath).extract()
        if len(datas) > index:
            return datas[index]
        elif len(datas) > 0:
            return "".join(datas)
        return default

    def find_browser_element_attr(self, browser=None, attr="text", *xpaths, **kwargs):
        if not browser or not xpaths:
            return None
        value = None
        for x in xpaths:
            try:
                element = browser.find_element_by_xpath(x)
                if attr == "text":
                    value = element.text
                else:
                    value = element.get_attribute(attr)
                if value:
                    break
            except NoSuchElementException as e:
                self.log(e)
        return value

    def find_browser_element(self, browser=None, *xpaths):
        if not browser or not xpaths:
            return None
        element = None
        for x in xpaths:
            try:
                element = browser.find_element_by_xpath(x)
                if element:
                    break
            except NoSuchElementException as e:
                element = None
                self.log(e)
        return element

    def find_browser_elements(self, browser=None, *xpaths):
        if not browser or not xpaths:
            return []
        elements = []
        for x in xpaths:
            try:
                elements = browser.find_elements_by_xpath(x)
                if elements:
                    break
            except NoSuchElementException as e:
                elements = []
                self.log(e)
        return elements


