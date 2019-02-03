""" Tests for "bucket_headerizer.py". """

import unittest

import mock

from s3headerize import BucketHeaderizer

# pylint: disable=no-self-use


@mock.patch('boto3.client')
@mock.patch('s3headerize.bucket_headerizer.ObjectHeaderizer')
class UpdateTestCase(unittest.TestCase):
    """ Tests for the "update" method. """

    def run_test(self, get_object_headerizer, get_client, key_prefix):
        """ Asserts that all objects are updated. """

        mock_client = mock.MagicMock()
        get_client.return_value = mock_client

        mock_paginator = mock.MagicMock()
        mock_client.get_paginator = mock.MagicMock(return_value=mock_paginator)

        mock_paginator.paginate = mock.MagicMock(return_value=[
            {
                'Contents': [
                    {
                        'Key': 'key-1'
                    },
                    {
                        'Key': 'key-2'
                    }
                ]
            },
            {
                'Contents': [
                    {
                        'Key': 'key-3'
                    }
                ]
            }
        ])

        header_rules = {}

        bucket_headerizer = BucketHeaderizer(header_rules=header_rules)

        bucket_headerizer.update(bucket='foo', key_prefix=key_prefix)

        get_object_headerizer.assert_has_calls(
            [
                mock.call(bucket='foo',
                          dry_run=False,
                          header_rules={},
                          key='key-1'),
                mock.call().update(),
                mock.call(bucket='foo',
                          dry_run=False,
                          header_rules={},
                          key='key-2'),
                mock.call().update(),
                mock.call(bucket='foo',
                          dry_run=False,
                          header_rules={},
                          key='key-3'),
                mock.call().update()
            ]
        )

    def test_updates_all_no_key_prefix(self,
                                       get_object_headerizer,
                                       get_client):
        """
        Asserts that all the objects are updated when no key prefix is
        specified.
        """
        self.run_test(get_object_headerizer=get_object_headerizer,
                      get_client=get_client,
                      key_prefix=None)

    def test_updates_all_with_key_prefix(self,
                                         get_object_headerizer,
                                         get_client):
        """
        Asserts that all the objects are updated when a key prefix is
        specified.
        """
        self.run_test(get_object_headerizer=get_object_headerizer,
                      get_client=get_client,
                      key_prefix='bar')
