# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import six
from sqlalchemy import exc
from scrapy.settings import Settings
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy.exceptions import DropItem
from scrapy.utils.misc import load_object
from ..exceptions import CrawledItemError, ScrapItemError
from ..item import CrawledItem, ScrapItem


class ItemPipeline(object):

    def __init__(self, enabled=None, settings=None):
        if not enabled:
            raise NotConfigured

    @classmethod
    def from_settings(cls, settings):
        enabled = settings['PROCESS_ITEM_ENABLED']
        return cls(enabled, settings=settings)

    def process_item(self, item, spider, **kwargs):
        func = getattr(spider, "process_item", None)
        if func and callable(func):
            try:
                item = func(item=item, spider=spider, **kwargs)
                if isinstance(item, CrawledItem):
                    raise DropItem("Crawled item found: %s" % item['url'])
                elif isinstance(item, ScrapItem):
                    raise DropItem("Scrap item found: %s" % item['url'])
            except CrawledItemError as e:
                spider.log(e, level=logging.INFO)
                raise DropItem(e)
            except ScrapItemError as e:
                spider.log(e, level=logging.INFO)
                raise DropItem(e)
            except exc.IntegrityError as e:
                spider.log(e, level=logging.ERROR)
                raise e
        return item
