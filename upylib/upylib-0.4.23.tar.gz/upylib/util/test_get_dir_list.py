#!/usr/bin/env python
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
from fs import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def test():
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    root = "../"
    print(root)
    dinfo_list = get_dir_list(root)
    if dinfo_list:
        for i, dinfo in enumerate(dinfo_list):
            print(dinfo.toJson())
            if i >= 3:
                break
    else:
        print("fail")

    print( "test recursive")
    root="../../"
    dinfo_list = get_dir_list(root, recursive=True)
    if dinfo_list:
        for i, dinfo in enumerate(dinfo_list):
            print(dinfo.toJson())
            if i >= 10:
                break
    else:
        print("fail")

    print( "test sort")
    dinfo_list = get_dir_list(root, recursive=True, ctx={ "sort": "dn", "order":"asc" })
    if dinfo_list:
        for i, dinfo in enumerate(dinfo_list):
            print(dinfo.full_dn)
            if i >= 10:
                break
    else:
        print("fail")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == "__main__": test()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
