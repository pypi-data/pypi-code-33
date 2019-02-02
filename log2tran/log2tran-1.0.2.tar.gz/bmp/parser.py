#!python
#coding:utf-8
#
# Module entry for log file parsers
#
__author__ = 'Aaron Tang(justforfun2000@msn.com)'

import sys
import os, shutil
import re

class FileParser(object):

    def __init__(self, fileProgram, fileDate):
        self.fileProgram=fileProgram
        self.fileDate=fileDate
        fileParser = fileProgram
        if not (os.path.isfile('./plugin/%s.py' % fileParser) or os.path.isfile('./plugin/%s.pyc' % fileParser)):
            fileParser = 'common'
        self.module=__import__('bmp.plugin.'+fileParser)
        # print('program: [%s]' % fileProgram)
        # dir(self.module)
        # dir(self.module.plugin)
        self.program = getattr(self.module.plugin, fileParser)

    def debug(self):
        print("%s:%s" % (self.program, self.info))

    def readLine(self, fp, prevChar):
        # print("In FileParser.read_line")
        # return fp.readline()
        return self.program.read_line(fp, prevChar)

    def writeLine(self, topDir, line):
        # dir(self.program)
        self.program.write_line(self.fileProgram, self.fileDate, topDir, line)

