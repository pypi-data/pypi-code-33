#! /usr/bin/env python3
"""
%(prog)s -- command line log file processor


USAGE: %(prog)s regexp1 regexp2 regexp3  <FILE

will generate a CSV with header with the matches (or None if no match) for each regexp as fields. If the regexp contain
a named group, the name of this group will be used as the header for the column. If not, any groups will be matched with the name "gn" (n=number starting with 0) as names.

Lines that fail to match all of the regular expressions provided will be discarded and echoed to STDERR.


Inspired by [RegExSerDe](https://github.com/apache/hive/blob/trunk/contrib/src/java/org/apache/hadoop/hive/contrib/serde2/RegexSerDe.java).

"""
import sys
import os
import re
from collections import Counter,defaultdict,OrderedDict, namedtuple
import csv

try :
    import pandas as pd
    import numpy as np
    has_pandas=True
except ImportError :
    has_pandas=False


maxbuffer=10000

class Converters:
    i   = lambda a: int(a) if a is not None else None
    f   = lambda a: float(a) if a is not None else None
    dezimal = lambda a: float(a.replace(".","").replace(",",".")) if a is not None else None
    decimal = lambda a: float(a.replace(",","")) if a is not None else None

    d = dezimal

def matchline(line, rexs):
    ngr = OrderedDict()
    gr = []
    notmatched = 0
    for r in rexs:
        m = r.search(line)
        if m:
            if m.groupdict():
                ngr.update(m.groupdict())
            elif m.groups():
                gr.extend(m.groups())
        else:
            notmatched += 1
    if gr:
        ngr.update({ "g%s" % a[0]: a[1] for a in enumerate(gr) })
    if notmatched:
        return {}
    else:
        return ngr



def process(argl) :
    buff=OrderedDict()
    rex = []
    proceed = True
    for a in argl:
        try:
            rex.append(re.compile(a))
        except Exception as e:
            sys.stderr.write(f"{e}: {a}\n")
            proceed = False
    if not proceed:
        sys.stderr.write("could not compile all regular expressions, see above\n")
        sys.exit()
    w=csv.writer(sys.stdout)
    headerrow=[]
    headerwritten=False
    ntclass = None
    ntkeys = None
    converter = {}
    for lineno,line in enumerate(sys.stdin.readlines()) :
        ngr = matchline(line, rex)
        if (ngr == {}) :
            sys.stderr.write("Unmatched line #%s: '%s'\n" % (lineno,line[:-1]))
        else:
            if ntclass is None:
                ntkeys = ngr.keys()
                ntclass = namedtuple('ntclass', ntkeys)
                for k in ntkeys:
                    if '_' in k:
                        parts = k.split("_")
                        if hasattr(Converters,parts[-1]):
                            converter[k] = getattr(Converters,parts[-1])
                        else:
                            cs = ", ".join((a for a in dir(Converters) if not a.startswith("_")))
                            sys.stderr.write(f"named group {k} references unknown converter {parts[-1]}. Possible values: {cs}")
            ed = { k: None for k in ntkeys }
            ed.update(ngr)
            for (k,c)in converter.items():
                ed[k]=c(ed[k])
            data = ntclass(**ed)
            if not headerwritten :
                w.writerow(ntkeys)
                headerwritten=True
            w.writerow(data)

def main():
    if len(sys.argv)<2 :
        print(__doc__ % dict(prog=sys.argv[0]))
    else :
        process(sys.argv[1:])

if __name__=='__main__' :
    main()

