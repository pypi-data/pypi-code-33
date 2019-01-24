#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename:    __init__.py
# @author:      yuanbin
# @github:      https://github.com/yuyuhupo
# @email:       yuanbin@fosun.com
# @Date:        2018/12/7 10:23
# @Copyright(©) 2018 by benyo.
__author__ = 'yuanbin'

import json
import time
import requests
import requests.auth
from .base import Base
from .host import Host
# from .host_group import HostGroup
from .item import Item
from .alert import Alert
from .trigger import Trigger
# from .dhost import Dhost
from .event import Event
from .trigger import Trigger
# from .httptest import HttpTest
# from .history import History


class ZabbixException(Exception):
    """exception:error"""
    pass


class ZabbixServerError(Exception):
    """5xx errors"""
    pass


class ZabbixClientError(Exception):
    """ Invalid input (4xx errors)"""
    pass


class ZabbixBadInputError(ZabbixClientError):
    """400"""
    pass


class ZabbixUnauthorizedError(ZabbixClientError):
    """401"""
    pass


class TokenAuth(requests.auth.AuthBase):
    """验证token有效性"""

    def __call__(self, r):
        r.header.update({"Authorization": "Brower {0}".format(self.token)})

    def __init__(self, token):
        self.token = token


class ZabbixApi(object):
    """zabbix应用接口"""

    def __init__(self, auth, zabbix_host, port, url_prefix, protocol, verify=True):
        self.auth = auth
        self.zabbix_host = zabbix_host
        self.port = port
        self.url_prefix = url_prefix
        self.protocol = protocol
        self.verify = verify
        self.headers = {"Content-Type": "application/json"}

        def url_construct():
            """zabbix Url: 组合url"""
            url_params = {
                'protocol': self.protocol,
                'host': self.zabbix_host,
                'port': port,
                'url_path_prefix': self.url_prefix
            }
            url_pattern = "{protocol}://{host}:{port}/{url_path_prefix}/api_jsonrpc.php"

            return url_pattern.format(**url_params)

        self.url = url_construct()
        self.r = requests

        def user_login(params):
            """登录"""
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": params[0],
                    "password": params[1]
                },
                "id": 0
            })
            response = requests.post(self.url, data=data, headers=self.headers)
            resp = json.loads(response.content)
            return resp.get('result', resp)

        self.auth_id = user_login(self.auth)

    def __getattr__(self, item_resource):
        def __request_runner(url, data, headers=None):
            runner = getattr(self.r, item_resource.lower())
            r = runner(url, data=data, headers=headers, auth=self.auth, verify=self.verify)
            if 500 <= r.status_code < 600:
                error_msg = "Server Error {0}: {1}".format(r.status_code, r.content.decode("ascii", "replace"))
                raise ZabbixServerError(error_msg)
            elif r.status_code == 400:
                error_msg = "Bad Input: `{0}`".format(r.text)
                raise ZabbixBadInputError(error_msg)
            elif r.status_code == 401:
                error_msg = "Unauthorized"
                raise ZabbixUnauthorizedError(error_msg)
            elif 400 <= r.status_code < 500:
                error_msg = "Client Error {0}: {1}".format(r.status_code, r.text)
                raise ZabbixClientError(error_msg)
            return r.json()

        return __request_runner
