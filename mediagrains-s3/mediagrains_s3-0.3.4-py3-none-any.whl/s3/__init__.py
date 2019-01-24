#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from S3 buckets

The primary interface is via the class GSFS3Bucket, although GSFS3Encoder can also be used
stand alone.
"""

from __future__ import print_function
from __future__ import absolute_import

from .encoder import GSFS3Encoder
from .gsfs3bucket import GSFS3Bucket

__all__ = ["GSFS3Encoder",
           "GSFS3Bucket"]
