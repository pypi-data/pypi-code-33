# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from ..utils.utilcls import DotDict, OrderedDotDict
from ..utils.logger import write_syslog
# noinspection PyUnresolvedReferences
from ..language import text


def send_serial(buffer):
    from atrader.tframe import sysclsbase as cnt

    tips = 'Send Data To ATCore'
    write_syslog(tips, level='debug', console=tips)
    return cnt.vr.g_ATraderSocket.send_data(buffer)


def recv_serial(tips=None):
    from atrader.tframe import sysclsbase as cnt

    tips = '`%s` Wait ATCore Response Data' % tips
    write_syslog(tips, level='debug', console=tips)
    return cnt.vr.g_ATraderSocket.read_tlv()


def send_serial_sub(buffer):
    from atrader.tframe import sysclsbase as cnt

    tips = 'Send SubData To ATCore'
    write_syslog(tips, level='debug', console=tips)
    return cnt.vr.g_ATraderSocketSub.send_data(buffer)


def recv_serial_sub(tips=None):
    from atrader.tframe import sysclsbase as cnt

    tips = '`%s` Wait ATCore Response SubData' % tips
    write_syslog(tips, level='debug', console=tips)
    return cnt.vr.g_ATraderSocketSub.read_tlv()
