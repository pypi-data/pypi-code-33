#!python
#coding:utf-8
#
# A program to scan BMP log directories, parse log files and grap key words to follow a transaction trail
#
import sys, os, argparse
import time, threading
import bmp.parser

def parseLogFile(trnDir, parentDir, filePath):
    print("Parsing file: %s" % filePath)
    _, fileProgram = os.path.split(parentDir)
    _, fileDate = os.path.splitext(filePath)
    fileDate = fileDate[1:]

    prevChar = ''
    fileParser = bmp.parser.FileParser(fileProgram, fileDate)
    fp = open(filePath, "r")
    try:
        while True:
            prevChar, line = fileParser.readLine(fp, prevChar)
            if not line:
                break
            if line[0] == '[':
                fileParser.writeLine(trnDir, line)
    finally:
        fp.close()

def scanDirectory(args):
    logDir, trnDir = args.logdir, args.trndir

    threads = []
    for parentDir, dirNames, fileNames in os.walk(logDir, followlinks=False):
        for i, fileName in enumerate(sorted(fileNames)):
            filePath = os.path.join(parentDir, fileName)
            # parseLogFile(trnDir, parentDir, filePath)
            t = threading.Thread(target=parseLogFile, args=( trnDir, parentDir, filePath, ))
            threads.append(t)
    for i, t in enumerate(threads):
        # t.setDaemon(True)
        t.start()
        if not i % args.threads:
            t.join()

def main():
    parser = argparse.ArgumentParser(description='Follow transaction trail.', prog='log2tran')
    parser.add_argument('--logdir', default=os.environ['HOME']+'/log',      help='root directory to scan')
    parser.add_argument('--trndir', default=os.environ['HOME']+'/logtran',  help='directory to store parsed transaction files')
    parser.add_argument('--threads', default=20,  help='threads number')
    args = parser.parse_args()

    scanDirectory(args)
    return 0

if __name__ == '__main__':
    sys.exit(main())

