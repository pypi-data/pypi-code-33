#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from Swift containers
"""

from __future__ import print_function
from __future__ import absolute_import

from mediagrains.gsf import loads

from ..bucket import GSFBucket
from .encoder import GSFSwiftEncoder
from ..progresstrackers import GSFDownloaderProgressTracker, GSFUploaderProgressTracker

__all__ = ["GSFSwiftBucket"]


class GSFSwiftBucket(GSFBucket):
    """A class representing an swift container. The constructor takes a container_name and a preconstructed
    swiftclient.Connection object.
    """
    def __init__(self, container_name, connection):
        super(GSFSwiftBucket, self).__init__()
        self.container_name = container_name
        self.connection = connection

    def get_encoder(self, key, cls=None, **kwargs):
        """Returns a GSFSwiftEncoder object which writes to a given object.
        :param key: an object key
        :param cls: the class to use for encoding, GSFSwiftEncoder is the default, others must inherit from it

        other keyword arguments will be fed to the class constructor.
        The object returned by this method will upload to the container when dump
        or end_dump is called."""
        if cls is None:
            cls = GSFSwiftEncoder
        if not issubclass(cls, GSFSwiftEncoder):
            raise TypeError("{!r} is not a subclass of {!r}".format(cls, GSFSwiftEncoder))
        progress_tracker = GSFUploaderProgressTracker(self.container_name, key)
        self.progress_trackers.append(progress_tracker)
        return cls(self.container_name,
                   key,
                   connection=self.connection,
                   upload_callback=progress_tracker,
                   **kwargs)

    def upload(self, key, grains, cls=None, segment_tags=None, **kwargs):
        """Serialise a series of grains into an object.
        :param key: an object key
        :param grains: an iterable of grain objects
        :param segment_tags: a list of pairs of strings to use as tags for the segment created
        :param cls: the class to use for encoding, GSFSwiftEncoder is the default, others must inherit from it

        other keyword arguments will be fed to the class constructor.
        This method will serialise the grains in a single segment."""

        enc = self.get_encoder(key, cls=cls, **kwargs)
        seg = enc.add_segment(tags=segment_tags)
        seg.add_grains(grains)
        # Nb. this will call start_dump and end_dump, so it actually starts the upload
        enc.dump()

    def download(self, key, cls=None, parse_grain=None, **kwargs):
        """Deserialise grains from a bucket into python, returns a
        pair of (head, segments) where head is a python dict containing general
        metadata from the file, and segments is a dictionary mapping numeric
        segment ids to lists of Grain objects.

        :param key: The object key
        :param cls: The class to use in decoding, the default is mediagrains.gsf.GSFDecoder
        :param parse_grain: A function that takes a (meta, data) tuple and returns a grain object
        the default is mediagrains.Grain

        Extra kwargs will be passed to the decoder constructor."""
        progress_tracker = GSFDownloaderProgressTracker(self.container_name, key)
        self.progress_trackers.append(progress_tracker)
        progress_tracker.max_size = self.connection.head_object(self.container_name, key)["contentlength"]
        (headers, body) = self.connection.get_object(self.container_name, key)
        progress_tracker.max_size = len(body)
        (head, grains) = loads(body, cls=cls, parse_grain=parse_grain, **kwargs)
        return (head, grains)
