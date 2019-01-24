#!/usr/bin/python
#
# Copyright 2018 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""\
Simple library for reading and writing grains to/from S3 buckets
"""

from __future__ import print_function
from __future__ import absolute_import

from io import BytesIO
from mediagrains.gsf import GSFEncoder
import boto3

__all__ = ["GSFS3Encoder"]


class GSFS3Encoder(GSFEncoder):
    """An encoder for GSF format which writes to an object in an S3 bucket.

    Derived from mediagrains.gsf.GSFEncoder.

    Constructor takes two mandatory arguments: a bucket name and an object key, optional arguments exist for specifying
    file-level metadata, if no created time is specified the current time will be used, if no id is specified one will
    be generated randomly.

    In addition the following optional arguments control S3 behaviour, they are passed through to calls to a
    boto3.client object, and for more details please consult the documentation for boto3:

    :param boto3_extra_args: object to be passed to the upload_fileobj call as ExtraArgs
    :param boto3_config: object to be passed to the upload_fileobj call as Config
    :param boto3_upload_callback: callable to be passed to the upload_fileobj call as Callback

    in particular the boto3_upload_callback object should be a callable which takes a single integer parameter, during
    the upload it will be called repeatedly with the number of bytes that have been transfered since the previous call.
    If the supplied callable object has a max_size attribute then the value of this will be set to the total expected
    size of the uploaded file just before uploading starts.

    The main interface are the methods add_grain and dump which add a grain to the file and dump the file to
    the S3 object respectively.

    You can instead use the "start_dump" method, followed by adding grains as needed, and then the "end_dump" method.
    In this mode the data will not be uploaded to S3 until end_dump is called.

    For further details please consult the documentation for mediagrains.gsf"""
    def __init__(self, bucket_name, object_key, boto3_extra_args=None, boto3_config=None, boto3_upload_callback=None,
                 boto3_client=None, major=7, minor=0, id=None, created=None, tags=None):
        self.boto3_client = boto3_client
        self.bucket_name = bucket_name
        self.object_key = object_key
        self.boto3_upload_callback = boto3_upload_callback
        self.boto3_extra_args = boto3_extra_args
        self.boto3_config = boto3_config
        if self.boto3_client is None:
            self.boto3_client = boto3.client('s3')
        fp = BytesIO()
        super(GSFS3Encoder, self).__init__(fp, major=major, minor=minor, id=id, created=created, tags=tags)

    def end_dump(self, all_at_once=False):
        """End the current dump and upload the results to S3."""
        super(GSFS3Encoder, self).end_dump(all_at_once=all_at_once)
        if hasattr(self.boto3_upload_callback, "max_size"):
            self.boto3_upload_callback.max_size = len(self.file.getvalue())
        self.file.seek(0)
        self.boto3_client.upload_fileobj(self.file, self.bucket_name, self.object_key,
                                         ExtraArgs=self.boto3_extra_args,
                                         Callback=self.boto3_upload_callback,
                                         Config=self.boto3_config)
