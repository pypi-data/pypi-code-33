#!python
#coding:utf-8
#
import sys, os
import re

def read_line(fp, prevChar):
    line = "%s%s"%(prevChar, fp.readline())
    if not line:
        # print("DEBUG return None")
        return '', None
    if line[0] != '[':
        # print("DEBUG return Not valid info[%s]" % line)
        return '', ' '

    # print("DEBUG Line: [%s]" % line)
    rec = re.compile('^\[(?P<trtime>\d\d:\d\d:\d\d) - (?P<pid>\d+)\](?P<logstr>.*)$')
    rem = rec.match(line)
    if not rem:
        return '', ' '
    keywords = rem.groupdict()
    logstr = keywords['logstr']
    if logstr:                              # normal log str
        # print("DEBUG return log str")
        return '', line

    # print("Ready to read hex Line: [%s]" % lin)
    hexLine = line[:-1] + "HEX:"            # add HEX for hex str
    while True:
        line = fp.readline(1)
        if not line:
            return '', hexLine+'\n'
        if line[0] == '[':
            return '[', hexLine+'\n'
        line2 = "%s%s" % (line, fp.readline())
        # print("hexLine: %s" % line2
        rec = re.compile('^..: (?P<hexstr>[0-9a-f\ ]+).*\[.*\]$')
        rem = rec.match(line2)
        if rem:
            hexInfo = rem.groupdict()
            hexLine = hexLine + hexInfo['hexstr'].replace(' ', '')
    return '', hexLine+'\n'


def write_line(fileProgram, fileDate, dstRoot, line):
    if line[0] != '[':
        return 
    rec = re.compile('^\[(?P<trtime>\d\d:\d\d:\d\d) - (?P<pid>\d+)\].*$')
    rem = rec.match(line)
    trnInfo = rem.groupdict()

    trtime = trnInfo['trtime']
    pid = trnInfo['pid']

    trnPath = "%s/%s/%s" % (dstRoot, fileProgram, fileDate)
    if not os.path.isdir(trnPath):
        os.makedirs(trnPath)
    trFilename="%s/%s-%s-%s.log" % (trnPath, fileProgram, fileDate, pid)

    trf = open (trFilename, "a+")
    try:
        trf.write(line)
    finally:
        trf.close()
