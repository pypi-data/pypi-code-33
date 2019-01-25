#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename:    item
# @author:      yuanbin
# @github:      https://github.com/yuyuhupo
# @email:       yuanbin@fosun.com
# @Date:        2018/12/7 11:37
# @Copyright(©) 2018 by benyo.
__author__ = 'yuanbin'

import json
from . import Base


class Item(Base):

    def __init__(self, api):
        super(Item, self).__init__(api)
        self.api = api

    def get(self, **kwargs):
        json_data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "webitems": True,
                "sortfield": ["itemid", "name"],
                # "applicationids": 2837,
                "filter": {"status": 0},
                "sortorder": "DESC"
            },
            "auth": self.api.auth_id,
            "id": 1
        }
        for k, v in kwargs.items():
            json_data['params'][k] = v

        data = json.dumps(json_data)
        response = self.api.POST(self.api.url, data=data, headers=self.api.headers)
        return True, response.get('result')

    def get_common(self, **kwargs):
        json_data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                # "filter": {"status": 0},
                "sortorder": "DESC"
            },
            "auth": self.api.auth_id,
            "id": 1
        }
        for k, v in kwargs.items():
            json_data['params'][k] = v

        data = json.dumps(json_data)
        response = self.api.POST(self.api.url, data=data, headers=self.api.headers)
        return True, response.get('result')
