"""
Applies headers to an S3 object.
"""

import logging

import boto3


class ObjectHeaderizer():
    """
    Applies headers to an S3 object.

    Args:
        header_rules (dict):      Header rules.
        key (str):                Key of the S3 object to update.
        dry_run (bool, optional): Perform a dry-run. Defaults to False.
    """

    def __init__(self, bucket, header_rules, key, dry_run=False):
        self._bucket = bucket
        self._dry_run = dry_run
        self._header_rules = header_rules
        self._key = key
        self._logger = logging.getLogger(__name__)
        self._new_cache_control = None
        self._new_content_type = None
        self._s3_object = None

    def _log_discovered_change(self, header, old_value, new_value):
        self._logger.info('%s: will update %s from "%s" to "%s".',
                          self._key,
                          header,
                          old_value,
                          new_value)

    def _apply_changes(self):
        client = boto3.client('s3')
        head = client.head_object(Bucket=self._bucket, Key=self._key)

        has_changes = False

        cache_control = head.get('CacheControl', None)

        if self._new_cache_control:
            if cache_control != self._new_cache_control:
                self._log_discovered_change(header='Cache-Control',
                                            old_value=cache_control,
                                            new_value=self._new_cache_control)
                has_changes = True
                cache_control = self._new_cache_control

        content_type = head.get('ContentType', None)

        if self._new_content_type and content_type != self._new_content_type:
            self._log_discovered_change(header='Content-Type',
                                        old_value=content_type,
                                        new_value=self._new_content_type)
            has_changes = True
            content_type = self._new_content_type

        if not has_changes:
            self._logger.info('%s: no changes.', self._key)
            return

        if self._dry_run:
            self._logger.info('%s: would apply changes now if not performing a'
                              'dry-run.',
                              self._key)
            return

        copy_object_args = {
            'Bucket': self._bucket,
            'Key': self._key,
            'CopySource': self._bucket + '/' + self._key,
            # Perform a fake replacement of the metadata, otherwise AWS will
            # reject the copy because nothing has changed. It doesn't notice
            # that the "ContentType" and/or "CacheControl" have changed.
            'Metadata': head['Metadata'],
            'MetadataDirective': 'REPLACE'
        }

        if content_type:
            copy_object_args['ContentType'] = content_type

        if cache_control:
            copy_object_args['CacheControl'] = cache_control

        client.copy_object(**copy_object_args)

    def _queue_change(self, header, value):
        if header == 'Content-Type':
            self._new_content_type = value
        elif header == 'Cache-Control':
            self._new_cache_control = value
        else:
            self._logger.warning('The "%s" header is not supported.', header)

    def _queue_changes(self, header_rule):
        header = header_rule['header']

        for when in header_rule['when']:
            if self._key.endswith(when['extension']):
                self._queue_change(header=header, value=when['then'])
                return

        else_value = header_rule.get('else', None)

        if else_value:
            self._queue_change(header=header, value=else_value)

    def update(self):
        """ Applies the relevant headers to this S3 object. """
        for header_rule in self._header_rules:
            self._queue_changes(header_rule=header_rule)
        self._apply_changes()
