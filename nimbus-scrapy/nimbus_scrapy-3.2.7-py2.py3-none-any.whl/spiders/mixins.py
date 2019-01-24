# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import sys
import logging
import json
from functools import wraps
from scrapy.http import Request
from scrapy.http import Response
from scrapy.utils.response import get_base_url

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException

from .. import utils

__all__ = [
    "UA_FIREFOX",
    "UA_SAFARI",
    "UA_PHANTOMJS",
    "BaseMixin",
    "SeleniumMixin",
]

UA_FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"
UA_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7"
UA_PHANTOMJS = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1"


class BaseMixin(object):
    name = None
    custom_settings = {
        "ITEM_PIPELINES": {
            'nimbus_scrapy.pipelines.ItemPipeline': 300,
        },
        "SPIDER_MIDDLEWARES": {
            'nimbus_scrapy.middlewares.DeltaFetch': 100,
        }
    }

    def get_base_url(self, response):
        return get_base_url(response=response)

    def parse_qs(self, query=None):
        return utils.parse_qs(query)

    def set_crawled(self, req, key):
        if not all([req, key]):
            raise ValueError("req and key not empty.")
        if isinstance(req, Request):
            request = req
            request.meta.update({'deltafetch_key': utils.md5(key)})
        elif isinstance(req, Response):
            request = req.request
            request.meta.update({'deltafetch_key': utils.md5(key)})

    def extract_xpath(self, sel, xpath, index=0, default=""):
        datas = sel.xpath(xpath).extract()
        if len(datas) > index:
            return datas[index]
        elif len(datas) > 0:
            return "".join(datas)
        return default


class SeleniumMixin(BaseMixin):
    DEFAULT_UA = UA_FIREFOX
    TIME_TO_WAIT = 30
    _webdriver = None
    _webproxy = None

    def closed(self, *args, **kwargs):
        self._close_browser()

    @property
    def webdriver(self):
        try:
            if self._webdriver is not None:
                return self._webdriver
            self._webdriver = self._get_webdriver(proxy=self._webproxy)
            return self._webdriver
        except SessionNotCreatedException as e:
            self._close_browser()
            return self._webdriver

    def new_webdriver(self, proxy=None, **kwargs):
        try:
            self._close_browser()
            self._webproxy = proxy
            self._webdriver = self._get_webdriver(proxy=self._webproxy, **kwargs)
            return self._webdriver
        except SessionNotCreatedException as e:
            self._close_browser()
            return self._webdriver

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

    def _get_capabilities(self, proxy=None, ua=None):
        ua = ua or self.DEFAULT_UA
        capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        capabilities["phantomjs.page.settings.userAgent"] = ua
        capabilities["phantomjs.page.customHeaders.User-Agent"] = ua
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
        capabilities = self._get_capabilities(proxy=proxy)
        driver = webdriver.PhantomJS(desired_capabilities=capabilities, **kwargs)
        driver.maximize_window()
        driver.implicitly_wait(self.TIME_TO_WAIT)
        driver.set_script_timeout(self.TIME_TO_WAIT)
        driver.set_page_load_timeout(self.TIME_TO_WAIT)
        return driver

    def _close_browser(self):
        try:
            if self._webdriver:
                self._webdriver.quit()
            self._webdriver = None
            self._webproxy = None
        except Exception as e:
            self._webdriver = None
            self._webproxy = None




