#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from fenrirscreenreader.core import debug

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
        self.macro = [[1,'KEY_LEFTSHIFT'],[1,'KEY_LEFTCTRL'],[1,'KEY_N'],[0.05,'SLEEP'],[0,'KEY_N'],[0,'KEY_LEFTCTRL'],[0,'KEY_LEFTSHIFT']]
    def shutdown(self):
        pass
    def getDescription(self):
        return 'No description found'         
    def run(self):
        self.env['runtime']['inputManager'].sendKeys(self.macro)
    def setCallback(self, callback):
        pass
