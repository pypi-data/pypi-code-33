# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
from collections import defaultdict
from scrapy.loader.processors import Join, MapCompose, TakeFirst, Identity
from scrapy.loader.processors import Compose, SelectJmes, MergeDict
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field
from multiprocessing import Process, Lock, Queue, current_process
from .callback.item import SpiderItemCallback


__all__ = [
    "CrawledItem",
    "ScrapItem",
    "FlexItem",
    "DeltaFetchItem",
    "FlexItemLoader",
    "SpiderItemCallback",
]


class CrawledItem(Item):
    url = Field()


class ScrapItem(Item):
    url = Field()


class FlexItem(Item):
    fields = defaultdict(Field)

    def __setitem__(self, key, value):
        if key not in self.fields:
            self.fields[key] = Field()
        super(FlexItem, self).__setitem__(key, value)


class DeltaFetchItem(FlexItem):
    deltafetch_key = Field()


class FlexItemLoader(ItemLoader):
    default_item_class = FlexItem



