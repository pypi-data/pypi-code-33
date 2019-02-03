"""
Applies headers to the matching objects within an S3 bucket.
"""

import logging

import boto3

from s3headerize import ObjectHeaderizer


class BucketHeaderizer():
    """
    Applies headers to the matching objects within an S3 bucket.

    Args:
        header_rules (dict):      Header rules.
        dry_run (bool, optional): Perform a dry-run. Defaults to False.
    """

    def __init__(self, header_rules, dry_run=False):
        self._dry_run = dry_run
        self._header_rules = header_rules
        self._logger = logging.getLogger(__name__)

    def update(self, bucket, key_prefix=None):
        """
        Applies headers to the matching objects within the S3 bucket.

        Args:
            bucket (str):               Name of the bucket.
            key_prefix (str, optional): Key prefix of objects to update,
        """

        client = boto3.client('s3')
        paginator = client.get_paginator('list_objects_v2')

        paginate_args = {
            'Bucket': bucket
        }

        if key_prefix:
            paginate_args['Prefix'] = key_prefix

        responses = paginator.paginate(**paginate_args)

        for response in responses:
            for s3_object in response['Contents']:
                o_h = ObjectHeaderizer(bucket=bucket,
                                       dry_run=self._dry_run,
                                       header_rules=self._header_rules,
                                       key=s3_object['Key'])
                o_h.update()
