# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import six
from inspect import isfunction, isclass
from sqlalchemy import exc
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy.exceptions import DropItem
from scrapy.utils.misc import load_object
from multiprocessing import Process, Lock, Queue, current_process
from ..exceptions import CrawledItemError, ScrapItemError
from ..item import CrawledItem, ScrapItem, SpiderItemCallback


class CallbackPipeline(object):

    def __init__(self, callback=None, lock=None, settings=None):
        if not callback:
            raise NotConfigured
        if isfunction(callback):
            self.callback = callback
        elif isclass(callback) and issubclass(callback, SpiderItemCallback):
            self.callback = callback()
        else:
            self.callback = None
            raise NotConfigured
        self.lock = Lock() if lock else None

    @classmethod
    def from_settings(cls, settings):
        callback = settings['ITEM_CALLBACK']
        lock = settings.getbool("ITEM_CALLBACK_LOCK", False)
        if isinstance(callback, six.string_types):
            callback = load_object(callback)
        return cls(callback, lock, settings=settings)

    def process_item(self, item, spider, **kwargs):
        self.acquire()
        try:
            if isinstance(self.callback, SpiderItemCallback):
                item = self.callback.process_item(item, spider, **kwargs)
            elif callable(self.callback):
                item = self.callback(item, spider, **kwargs)
        finally:
            self.release()
        yield item

    def acquire(self):
        try:
            if self.lock:
                self.lock.acquire()
        except Exception as e:
            pass

    def release(self):
        try:
            if self.lock:
                self.lock.release()
        except Exception as e:
            pass
