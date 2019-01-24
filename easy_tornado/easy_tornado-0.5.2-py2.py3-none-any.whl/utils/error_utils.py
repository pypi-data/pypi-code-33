# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018年8月23日 14:26:49
from . import error_handler
from .error_handler import error_exit
from ..compat import happy_move_functions

happy_move_functions(error_handler, error_exit)
