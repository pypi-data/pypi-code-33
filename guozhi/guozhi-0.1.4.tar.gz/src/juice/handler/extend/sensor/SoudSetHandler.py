#!/usr/bin/env python
# -*- coding:utf-8 -*-

from juice.handler.PropSetHandler import PropSetHandler
from juice.model.PropMessage import PropMessage


class SoudSetHandler(PropSetHandler):
    """
        蜂鸣器设置方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, prop_message):
        self.reply(PropMessage(prop_message.flag, True))
