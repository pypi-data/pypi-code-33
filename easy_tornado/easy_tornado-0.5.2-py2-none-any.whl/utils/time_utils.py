# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018年8月23日 14:26:49
from . import time_extension
from .time_extension import Timer
from .time_extension import current_datetime
from .time_extension import current_datetime_str
from .time_extension import current_datetime_str_s
from .time_extension import current_timestamp
from ..compat import happy_move_functions

happy_move_functions(time_extension,
                     current_timestamp, current_datetime,
                     current_datetime_str, current_datetime_str_s,
                     Timer)
