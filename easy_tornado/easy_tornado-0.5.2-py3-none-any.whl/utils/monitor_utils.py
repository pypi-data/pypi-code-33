# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/6 14:05
from . import monitoring
from .monitoring import kill_process
from ..compat import happy_move_functions

happy_move_functions(monitoring, kill_process)
