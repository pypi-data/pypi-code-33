# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals


class SpiderItemCallback(object):

    def process_item(self, item, spider=None, *args, **kwargs):
        raise NotImplementedError
