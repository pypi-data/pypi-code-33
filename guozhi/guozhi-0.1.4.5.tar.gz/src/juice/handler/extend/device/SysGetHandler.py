#!/usr/bin/env python
# -*- coding:utf-8 -*-

from juice.handler.PropHandler import PropGetHandler
from juice.model.PropMessage import PropMessage
from juice.util import Util


class SysArmGetHandler(PropGetHandler):
    """
        系统CPU内存占比响应方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, Util.get_raspberry_prop_info("get_mem_arm")))


class SysGpuGetHandler(PropGetHandler):
    """
        系统GPU内存占比响应方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, Util.get_raspberry_prop_info("get_mem_gpu")))


class SysVoltsGetHandler(PropGetHandler):
    """
        系统核心电压响应方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, Util.get_raspberry_prop_info("measure_volts_core")))


class SysTempGetHandler(PropGetHandler):
    """
        温度响应方法
        handle为必须实现的方法
        reply上行消息，返回给服务器
    """

    def handle(self, flag):
        self.reply(PropMessage(flag, Util.get_raspberry_prop_info("measure_temp")))
