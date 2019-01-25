#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename:    host
# @author:      yuanbin
# @github:      https://github.com/yuyuhupo
# @email:       yuanbin@fosun.com
# @Date:        2018/12/7 11:31
# @Copyright(©) 2018 by benyo.
__author__ = 'yuanbin'

import json
from . import Base


class Host(Base):
    """主机"""
    def __init__(self, api):
        super(Host, self).__init__(api)
        self.api = api

    def get(self, **kwargs):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {"output": "extend", "filter": {}},
            "auth": self.api.auth_id,
            "id": 1
        }
        for k, v in kwargs.items():
            if k in ['status', 'hostid', 'host', '']:
                data['params']['filter'][k] = v
            else:
                data['params'][k] = v

        data_str = json.dumps(data)
        response = self.api.POST(self.api.url, data=data_str, headers=self.api.headers)
        return True, response.get('result')
