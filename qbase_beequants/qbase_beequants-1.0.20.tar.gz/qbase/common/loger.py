#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

import logging
import logging.handlers
import sys

class Loger:

    '''
    initLog: init loger return a loger
    AppName: application name ,logname is ${AppName}.log
    logLevel: DEBUG[debug],INFO[info]
    '''
    def __init__(self, filePath, logLevel):
        #获取logger实例，如果参数为空则返回root logger
        self.loger = logging.getLogger()

        # 指定logger输出格式
        formatter = logging.Formatter('[%(asctime)s]%(levelname)s[%(threadName)s][%(filename)s:%(lineno)d]: %(message)s')

        # 文件日志
        file_handler = logging.handlers.TimedRotatingFileHandler(filePath, when='D', interval=1, encoding='utf8')
        file_handler.suffix = "%Y-%m-%d_%H-%M-%S"

        file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
        self.loger.addHandler(file_handler)

        if logLevel == 'DEBUG' or logLevel == 'debug':
            # 控制台日志
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.formatter = formatter  # 也可以直接给formatter赋值
            self.loger.addHandler(console_handler)
            # 指定日志的最低输出级别
            self.loger.setLevel(logging.DEBUG)
        elif logLevel == 'INFO' or logLevel == 'info':
            # 指定日志的最低输出级别
            self.loger.setLevel(logging.INFO)
        elif logLevel == 'WARNING' or logLevel == 'warning':
            self.loger.setLevel(logging.WARNING)
        elif logLevel == 'ERROR' or logLevel == 'error':
            self.loger.setLevel(logging.ERROR)
        else:
            self.loger.setLevel(logging.INFO)

    def getLoger(self):
        return self.loger

