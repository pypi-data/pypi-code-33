#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename:    __init__.py
# @author:      yuanbin
# @github:      https://github.com/yuyuhupo
# @email:       yuanbin@fosun.com
# @Date:        2018/12/7 10:20
# @Copyright(©) 2018 by benyo.
__author__ = 'yuanbin'


from lib import *


class ZabbixFace(object):

    def __init__(self, auth=(), zabbix_host="", port=80, url_prefix="zabbix", protocol="http", verify=True):
        self.api = ZabbixApi(auth,
                             zabbix_host=zabbix_host,
                             port=port,
                             url_prefix=url_prefix,
                             protocol=protocol,
                             verify=verify)

    def __getattr__(self, item_resource):
        for cls in Base.__subclasses__():
            if cls.__name__.lower() == item_resource:
                return cls(api=self.api)
        return


class TestZabbixFace(object):

    def __init__(self):
        pass

    def test_zabbix_api(self):
        params = {'hostids': "10288"}
        cli = ZabbixFace(('Admin', 'Fosun+_)(*2018'))
        cli.host.get(**params)
