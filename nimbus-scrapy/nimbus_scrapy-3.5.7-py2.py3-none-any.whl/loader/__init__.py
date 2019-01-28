# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals

from scrapy.loader import ItemLoader
from ..item import FlexItemLoader, FlexItem
from .processors import MapComposeDefault, TakeFirstDefault, DTFormat, TakeSecond


