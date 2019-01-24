# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018年8月23日 14:26:49
from . import str_extension
from .str_extension import md5sum
from .str_extension import parse_json
from ..compat import happy_move_functions

happy_move_functions(str_extension, md5sum, parse_json)
