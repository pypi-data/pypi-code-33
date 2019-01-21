#!/usr/bin/env python
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
from fs import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def test():
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    print("test")
    ext = extract_ext("a.mp4")
    print(ext)
    print( is_movie("a.mp4") )
    print( is_image("a.mp4") )
    print( is_music("a.mp4") )

    ext = extract_ext("~/.bashrc")
    print(ext)

    print( is_text("/home/windnc/test.txt") )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == "__main__": test()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
