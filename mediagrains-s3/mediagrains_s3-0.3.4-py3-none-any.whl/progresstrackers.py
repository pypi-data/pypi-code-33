#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Components for tracking ongoing progress of transfers to S3 buckets
"""

from __future__ import print_function
from __future__ import absolute_import

__all__ = ["GSFProgressTracker", "GSFDownloaderProgressTracker", "GSFUploaderProgressTracker"]


class GSFProgressTracker(object):
    """A simple object which can be used to keep track of progress of an ongoing transfer."""
    def __init__(self, bucket_name, key):
        self.bucket_name = bucket_name
        self.key = key
        self.progress = 0
        self.max_size = -1
        self.direction = None
        self.__transfering = "".format(self.bucket_name, self.key)
        self.__transfered = "transfered to/from {}:{}".format(self.bucket_name, self.key)

    def __call__(self, progress):
        self.progress += progress

    def __repr__(self):
        if self.direction == "up":
            transfering = "uploading to"
            transfered = "uploaded to"
        elif self.direction == "down":
            transfering = "downloading from"
            transfered = "downloaded from"
        else:
            transfering = "transfering from/to"
            transfered = "transfered from/to"
        if self.max_size == -1:
            return "<{} {}:{}, {} bytes>".format(transfering,
                                                 self.bucket_name,
                                                 self.key,
                                                 self.progress)
        elif self.progress < self.max_size:
            return "<{} {}:{}, {}/{} bytes>".format(transfering,
                                                    self.bucket_name,
                                                    self.key,
                                                    self.progress,
                                                    self.max_size)
        else:
            return "<{} {}:{}, {} bytes>".format(transfered,
                                                 self.bucket_name,
                                                 self.key,
                                                 self.max_size)


class GSFDownloaderProgressTracker(GSFProgressTracker):
    """A simple object which can be used to keep track of progress of an ongoing download."""
    def __init__(self, bucket_name, key):
        super(GSFDownloaderProgressTracker, self).__init__(bucket_name, key)
        self.direction = "down"


class GSFUploaderProgressTracker(GSFProgressTracker):
    """A simple object which can be used to keep track of progress of an ongoing upload."""
    def __init__(self, bucket_name, key):
        super(GSFUploaderProgressTracker, self).__init__(bucket_name, key)
        self.direction = "up"
