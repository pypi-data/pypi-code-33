#!/usr/bin/env python
# -*- coding:utf-8 -*-

from juice.handler.PropGetHandler import PropGetHandler
from juice.model.PropMessage import PropMessage
from juice.util import Util


class TempGetHandler(PropGetHandler):
    """
        温度响应方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, Util.get_raspberry_prop_info("measure_temp")))
