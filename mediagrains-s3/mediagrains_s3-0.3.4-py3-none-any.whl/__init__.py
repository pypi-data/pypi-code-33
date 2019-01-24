#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from object storage buckets

The primary interface is via the class GSFS3Bucket, although GSFS3Encoder can also be used
stand alone.
"""

from __future__ import print_function
from __future__ import absolute_import

from .s3.encoder import GSFS3Encoder
from .s3.gsfs3bucket import GSFS3Bucket
from .progresstrackers import GSFDownloaderProgressTracker, GSFUploaderProgressTracker, GSFProgressTracker

__all__ = ["GSFS3Encoder",
           "GSFS3Bucket",
           "GSFDownloaderProgressTracker",
           "GSFUploaderProgressTracker",
           "GSFProgressTracker",
           "GSFS3DownloaderProgressTracker",
           "GSFS3UploaderProgressTracker",
           "GSFS3ProgressTracker"]

GSFS3ProgressTracker = GSFProgressTracker
GSFS3DownloaderProgressTracker = GSFDownloaderProgressTracker
GSFS3UploaderProgressTracker = GSFUploaderProgressTracker


def main():  # pragma: no cover
    from sys import argv, exit
    from uuid import UUID
    from mediagrains import VideoGrain
    from mediagrains.cogenums import CogFrameFormat, CogFrameLayout
    import time
    import threading

    if len(argv) < 3:
        print("usage: {} <bucket_name> <key>".format(argv[0]))
        exit(1)

    bucket_name = argv[1]
    key = argv[2]

    src_id = UUID("8e891446-2d12-11e8-b7c0-dca904824eec")
    flow_id = UUID("9541123e-2d12-11e8-ba8a-dca904824eec")

    grains = [VideoGrain(src_id, flow_id,
                         cog_frame_format=CogFrameFormat.S16_422_10BIT,
                         cog_frame_layout=CogFrameLayout.FULL_FRAME)
              for _ in range(0, 1)]

    bucket = GSFS3Bucket(bucket_name)

    t = threading.Thread(target=bucket.upload, args=(key, grains))
    t.daemon = True
    t.start()

    completed = []
    old_p = 0
    while len(completed) == 0:
        (k, (d, p, n)) = list(bucket.progress().items())[0]
        if p != old_p:
            print("{}:{} ({}): {}/{} bytes".format(bucket_name, k, d, p, n))
            old_p = p
        completed = bucket.purge_completed()
        time.sleep(0.1)

    class DL(object):
        def __init__(self, bucket, key):
            self.bucket = bucket
            self.key = key
            self.head = None
            self.segments = None

        def __call__(self):
            (self.head, self.segments) = self.bucket.download(self.key)

    dl = DL(bucket, key)
    t = threading.Thread(target=dl)
    t.daemon = True
    t.start()

    completed = []
    old_p = 0
    while len(completed) == 0:
        (k, (d, p, n)) = list(bucket.progress().items())[0]
        if p != old_p:
            print("{}:{} ({}): {}/{} bytes".format(bucket_name, k, d, p, n))
            old_p = p
        completed = bucket.purge_completed()
        time.sleep(0.1)

    print((dl.head, dl.segments))
