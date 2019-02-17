# -*- coding:utf-8 -*-

import os
from SCLibrary.builtin import ValidatorKeywords
from SCLibrary.builtin import RequesterKeywords
from SCLibrary.builtin import DBKeywords
from SCLibrary.builtin import LogListener
from SCLibrary.builtin import RandomKeywords
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from SCLibrary.base import DynamicCore, hook_zh

__version__ = '0.6.11'


class SCLibrary(DynamicCore):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        libraries = [ValidatorKeywords(), RequesterKeywords(),
                     DBKeywords(), RandomKeywords()]
        DynamicCore.__init__(self, libraries)
        built_in = BuiltIn()
        if built_in.get_variable_value("${RF_DEBUG}") == True:
            self.ROBOT_LIBRARY_LISTENER = LogListener()
        # 复写robot的unic.py，支持Log打印中文
        # hook_zh()
