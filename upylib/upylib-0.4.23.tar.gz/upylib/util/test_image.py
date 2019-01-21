#!/usr/bin/env python3
# -*- coding:utf-8 -*-⏎
from image import *
from fs import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def test():
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    src_fn="a.jpg"
    dst_fn="a.thumb.jpg"
    size = (120,100)
    print("a.jpg")
    if save_thumb(src_fn, dst_fn, size):
        print("ok")
    else:
        print("no")

    src_fn="b.jpg"
    dst_fn="b.thumb.jpg"
    size = (120,100)
    print("b.jpg")
    if save_thumb(src_fn, dst_fn, size):
        print("ok")
    else:
        print("no")

    src_fn="c.jpg"
    dst_fn="c.thumb.jpg"
    print("c.jpg")
    size = (120,100)
    if save_thumb(src_fn, dst_fn, size):
        print("ok")
    else:
        print("no")

    src_fn="a.png"
    dst_fn="a.thumb.png.jpg"
    print("a.png")
    size = (120,100)
    if save_thumb(src_fn, dst_fn, size):
        print("ok")
    else:
        print("no")

    src_fn="c.png"
    dst_fn="c.thumb.png.jpg"
    size = (120,100)
    if save_thumb(src_fn, dst_fn, size):
        print("ok")
    else:
        print("no")

if __name__ == "__main__": test()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
