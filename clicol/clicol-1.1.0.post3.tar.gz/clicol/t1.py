#!/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes

a=bytes(b"asd")
print(repr(a))
a+=b"qwe"
print(repr(a))
