#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from Swift containers

The primary interface is via the class GSFSwiftBucket, although GSFSwiftEncoder can also be used
stand alone.
"""

from __future__ import print_function
from __future__ import absolute_import

from .encoder import GSFSwiftEncoder
from .gsfswiftbucket import GSFSwiftBucket

__all__ = ["GSFSwiftEncoder",
           "GSFSwiftBucket"]
