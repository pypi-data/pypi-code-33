# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/8/27 15:26
from . import coll_extension
from .coll_extension import unique_list
from ..compat import happy_move_functions

happy_move_functions(coll_extension, unique_list)
