#! /usr/bin/env python3
"""
%(prog)s -- command line data science


USAGE: %(prog)s regexp  <FILE


%(prog)s will concatenate lines matching certain criteria from STDIN to a tab-separated single line on stdout

Criteria can be: matching regexp

BUG: Max. 10.000 groups are supported - there should be a command line switch for that,
and/or a way to store more groups on disk.


"""
import sys
import os
import re
from collections import Counter,defaultdict,OrderedDict
import csv

try :
    import pandas as pd
    import numpy as np
    has_pandas=True
except ImportError :
    has_pandas=False


maxbuffer=10000

def writeobj(d,k) :
    sys.stdout.write(str(k)+"\t"+str(len(d[k][1]))+"\t"+"\t".join(d[k][1])+"\n")


def process(arg) :
    buff=OrderedDict()
    rex=re.compile(arg)
    linecounter=0
    seen=set()
    for line in sys.stdin.readlines() :
        linecounter+=1
        line=line[:-1]
        m=rex.search(line)
        if m :
            key=m.group()
        else :
            key=None
        if key in buff :
            buff[key][0]=linecounter
            buff[key][1].append(line)
        else :
            buff[key]=[linecounter,[line]]
            if key in seen :
                sys.stderr.write("Please increase buffer size from current value of {}. Key {} was found after being flushed\n".format(maxbuffer,key))
        if len(buff.keys())>maxbuffer :
            sk=sorted([(k,v[0]) for (k,v) in buff.items()],key=lambda a: a[1])[0]
            writeobj(buff,sk[0])
            del buff[sk[0]]
            seen.add(sk[0])
    for k in buff.keys() :
        writeobj(buff,k)


def main():
    if len(sys.argv)<2 :
        print(__doc__ % dict(prog=sys.argv[0]))
    else :
        process(sys.argv[1])

if __name__=='__main__' :
    main()


