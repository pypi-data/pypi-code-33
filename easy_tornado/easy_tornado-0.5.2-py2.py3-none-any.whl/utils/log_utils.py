# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/10/30 14:29
from . import logging
from .logging import it_print
from .logging import it_prints
from ..compat import happy_move_functions

happy_move_functions(logging, it_print, it_prints)
