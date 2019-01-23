#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

"""

   环境配置

   默认使用开发环境参数

   运行参数带 --prod 的时候使用生产环境参数

"""

import sys
import configparser


class configer:
    # 默认使用开发环境
    __configFIle = 'conf/configDev.ini'
    __confger = None

    def __init__(self):
        if len(sys.argv) > 1:
            for x in sys.argv[1:]:
                if x == "--prod":
                    self.__configFIle = 'conf/configProd.ini'
                    break

        self.__confger = configparser.ConfigParser()
        self.__confger.read(self.__configFIle)

    def getConfiger(self):
        return self.__confger

    def getOption(self,option):
        return self.__confger.options(option)

    def getValueByKey(self, section, option):
        return self.__confger.get(section, option)
