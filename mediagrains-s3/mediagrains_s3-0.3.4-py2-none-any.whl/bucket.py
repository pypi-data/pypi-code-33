#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from object storage buckets

Abstract base class for bucket implementations
"""

from __future__ import print_function
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod

__all__ = ["GSFBucket"]


class GSFBucket:
    """An abstract base-class representing an object storage bucket.

    This class should never be instantiated directly.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.progress_trackers = []

    @abstractmethod
    def get_encoder(self, key, cls=None, **kwargs):
        """Returns a GSFEncoder object which writes to an object in this bucket.
        :param key: an object key
        :param cls: the class to use for encoding, subclasses will supply different default values

        other keyword arguments will be fed to the class constructor.
        The object returned by this method will upload to the bucket when dump
        or end_dump is called."""
        pass

    @abstractmethod
    def upload(self, key, grains, cls=None, segment_tags=None, **kwargs):
        """Serialise a series of grains into an object in this bucket.
        :param key: an object key
        :param grains: an iterable of grain objects
        :param segment_tags: a list of pairs of strings to use as tags for the segment created
        :param cls: the class to use for encoding

        other keyword arguments will be fed to the class constructor.
        This method will serialise the grains in a single segment."""
        pass

    @abstractmethod
    def download(self, key, cls=None, parse_grain=None, **kwargs):
        """Deserialise grains from an object storage bucket into python, returns a
        pair of (head, segments) where head is a python dict containing general
        metadata from the file, and segments is a dictionary mapping numeric
        segment ids to lists of Grain objects.

        :param key: The object key
        :param cls: The class to use in decoding
        :param parse_grain: A function that takes a (meta, data) tuple and returns a grain object
        the default is mediagrains.Grain

        Extra kwargs will be passed to the decoder constructor."""
        pass

    def progress(self):
        """Returns a dictionary reporting the progress of ongoing uploads."""
        return {t.key: (t.direction, t.progress, t.max_size) for t in self.progress_trackers}

    def purge_completed(self):
        """Removes progress tracking for completed uploads, and returns a list of
        progress trackers that have been removed from the active list."""
        completed = []
        for t in self.progress_trackers:
            if t.progress == t.max_size:
                self.progress_trackers.remove(t)
                completed.append(t)
        return completed
