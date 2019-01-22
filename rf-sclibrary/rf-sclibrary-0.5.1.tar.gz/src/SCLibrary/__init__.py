# -*- coding:utf-8 -*-

import os
from SCLibrary.builtin import ValidatorKeywords
from SCLibrary.builtin import RequesterKeywords
from SCLibrary.builtin import DBKeywords
from SCLibrary.builtin import LogListener
from robot.libraries.BuiltIn import BuiltIn
from SCLibrary.base import DynamicCore, hook_zh

__version__ = '0.5.1'


class SCLibrary(DynamicCore):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__
 
    def __init__(self):
        libraries = [ValidatorKeywords(), RequesterKeywords(), DBKeywords()]
        DynamicCore.__init__(self, libraries)
        built_in = BuiltIn()
        try:
            exec_dir = built_in.get_variable_value("${EXECDIR}")
            env = built_in.get_variable_value("${RF_ENV}")
            built_in.set_global_variable("${ENVDIR}", '%s/config/%s.env.robot' % (exec_dir, env))
            if built_in.get_variable_value("${RF_DEBUG}") == True:
                self.ROBOT_LIBRARY_LISTENER = LogListener()
        except:
            pass
        # 复写robot的unic.py，支持Log打印中文
        # hook_zh()