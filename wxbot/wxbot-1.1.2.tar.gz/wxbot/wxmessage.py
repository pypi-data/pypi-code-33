# -*- coding:utf-8 -*-

__author__ = "cfn@leapy.cn"

from wxbot import wxconf
import logging
import os
import time

# debug 模式不输出错误信息
class message(object):

    def __init__(self):
        self.debug = wxconf.WXConf().baseconf['debug']
        self.log = wxconf.WXConf().baseconf['log']
        self.logPath = wxconf.WXConf().baseconf['logPath']

    # 错误信息
    def error(self, *params):
        if self.debug:
            print(self.message("执行出错：", params))
        else:
            self.message("执行出错：", params)

    # 成功信息
    def success(self, *params):
        if self.debug:
            print(self.message("执行成功：", params))
        else:
            self.message("执行成功：", params)

    # 信息提示
    def notice(self, *params):
        if self.debug:
            print(self.message("提示信息：", params))
        else:
            self.message("提示信息：", params)

    # 致命错误
    def fadal(self,*params):
        if self.debug:
            print(self.message("致命错误：", params))
        else:
            self.message("致命错误：", params)

    def message(self, _msg, params):
        msg = '['+time.strftime('%Y-%m-%d %H:%M:%S')+']' + ' '+_msg
        for i in params:
            msg += str(i) + ' '
        msg += "\n"

        # 写入日志
        if self.log:
            self.writelog(msg)

        return msg

    # 写日志
    def writelog(self, msg):

        # 判断文件夹是否存在，不存在则创建
        if os.path.exists(self.logPath) == -2:
            os.makedirs(self.logPath)

        # 如果存在文件，写入
        if os.path.exists(self.logPath):
            path = self.logPath + time.strftime('%Y-%m-%d') + '.log'
            file = open(path, 'a+', encoding='utf-8')
            file.write(msg)
            file.close()