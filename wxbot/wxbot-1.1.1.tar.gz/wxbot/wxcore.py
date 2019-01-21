# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

from wxbot import wxparse
from wxbot import wxmessage,wxmail
import subprocess


class core():

    def __init__(self):
        wxmessage.message.__init__(self)
        self.wx = wxparse.parse()

    def WxRun(self):
        self.wx.login()



def wxRun():
    c = core()
    c.WxRun()

def wxCMD():
    pass


wxRun()