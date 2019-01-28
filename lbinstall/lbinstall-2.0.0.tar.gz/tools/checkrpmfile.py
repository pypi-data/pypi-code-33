#!/usr/bin/env python
import lbinstall.rpmfile as rpmfile
import sys

# rpm = rpmfile.open("/home/lben/TestRpm-1.0-1.x86_64.rpm")
rpm = rpmfile.open(sys.argv[1])

# m = rpm.getmember("./opt/LHCb/TestRpm/mydir/toto.py")
# f = rpm.extractfile(m)
# print(f.read())

filesizes = rpm._headers["filesizes"]

# from pprint import pprint
# pprint(rpm._headers)
for i, m in enumerate(rpm.getmembers()):
    vals = [m.name]
    for k, v in m._attrs.items():
        vals.append(k + ":" + str(v))
    vals.append("size:" + str(m.size))
    vals.append("metadatasize:" + str(filesizes[i]))
    if not m._attrs["isDir"] and m.size != filesizes[i]:
        print(", ".join(vals))
