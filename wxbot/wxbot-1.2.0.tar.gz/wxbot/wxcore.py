# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

from wxbot import wxparse
from wxbot import wxconf
import sys

def wxRun():
    argv = sys.argv[-1]
    if argv == '-v' or argv == '--version':
        print(wxconf.WXConf().baseconf['version'])
    elif argv == '-h' or argv == '--help':
        print(wxconf.WXConf().baseconf['help'])
    else:
        wxparse.parse().login()