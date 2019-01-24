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

from io import BytesIO
from mediagrains.gsf import GSFEncoder

__all__ = ["GSFSwiftEncoder"]


class GSFSwiftEncoder(GSFEncoder):
    """An encoder for GSF format which writes to an object in an Swift Container.

    Derived from mediagrains.gsf.GSFEncoder.

    Constructor takes three mandatory arguments: a container name and an object key, optional arguments exist for
    specifying file-level metadata, if no created time is specified the current time will be used, if no id is
    specified one will be generated randomly.

    :param connection: a swiftclient.Connection object

    The main interface are the methods add_grain and dump which add a grain to the file and dump the file to
    the object respectively.

    You can instead use the "start_dump" method, followed by adding grains as needed, and then the "end_dump" method.
    In this mode the data will not be uploaded to Swift until end_dump is called.

    For further details please consult the documentation for mediagrains.gsf"""
    def __init__(self, container_name, object_key, connection=None, upload_callback=None,
                 major=7, minor=0, id=None, created=None, tags=None):
        self.connection = connection
        self.container_name = container_name
        self.object_key = object_key
        self.upload_callback = upload_callback
        fp = BytesIO()
        super(GSFSwiftEncoder, self).__init__(fp, major=major, minor=minor, id=id, created=created, tags=tags)

    def end_dump(self, all_at_once=False):
        """End the current dump and upload the results to Swift."""
        super(GSFSwiftEncoder, self).end_dump(all_at_once=all_at_once)
        body = self.file.getvalue()
        length = len(body)
        if hasattr(self.upload_callback, "max_size"):
            self.upload_callback.max_size = length
        self.file.seek(0)
        self.connection.put_object(self.container_name, self.object_key, self.file,
                                   content_length=length, content_type="video/x-gsf")
