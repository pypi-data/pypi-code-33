#!/usr/bin/env python
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
from fs import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def test():
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    print( "test dinfo")
    dinfo = DirInfo( full_dn="/home/windnc" )
    print(dinfo.toJson())

    print( "test dinfo")
    dinfo = DirInfo( path="/home", dn="windnc" )
    print(dinfo.toJson())

    print( "test get_dir_list" )
    dinfo_list = get_dir_list( "/home/windnc" )
    for dinfo in dinfo_list:
        print( dinfo.toJson() )


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == "__main__": test()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
