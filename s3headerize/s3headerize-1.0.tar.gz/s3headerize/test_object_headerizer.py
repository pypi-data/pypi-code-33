""" Tests for "object_headerizer.py". """

import unittest

import mock

from s3headerize import ObjectHeaderizer

# pylint: disable=no-self-use


@mock.patch('boto3.client')
class ApplyChangesTestCase(unittest.TestCase):
    """ Tests for the "_apply_changes" method. """

    def test_cache_control_changed_from_previous_value(self, get_client):
        """
        Asserts that the Cache-Control value can be changed from an existing
        value.
        """

        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'CacheControl': 'cache-control-foo',
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar')

        o_h._new_cache_control = 'cache-control-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_called_with(
            Bucket='foo',
            CacheControl='cache-control-bar',
            CopySource='foo/bar',
            Key='bar',
            Metadata={
                'meta-foo': 'meta-bar'
            },
            MetadataDirective='REPLACE'
        )

    def test_content_type_changed_from_previous_value(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'ContentType': 'content-type-foo',
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar')

        o_h._new_content_type = 'content-type-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_called_with(
            Bucket='foo',
            ContentType='content-type-bar',
            CopySource='foo/bar',
            Key='bar',
            Metadata={
                'meta-foo': 'meta-bar'
            },
            MetadataDirective='REPLACE'
        )

    def test_content_type_changed_from_previous_value_in_dry_run(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'ContentType': 'content-type-foo',
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        object_headerizer = ObjectHeaderizer(bucket='foo',
                                             dry_run=True,
                                             header_rules=[],
                                             key='bar')

        object_headerizer._new_content_type = 'content-type-bar'  # pylint: disable=protected-access
        object_headerizer._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_not_called()

    def test_cache_control_changed_from_none(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar')
        o_h._new_cache_control = 'cache-control-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_called_with(
            Bucket='foo',
            CacheControl='cache-control-bar',
            CopySource='foo/bar',
            Key='bar',
            Metadata={
                'meta-foo': 'meta-bar'
            },
            MetadataDirective='REPLACE'
        )

    def test_content_type_changed_from_none(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar')
        o_h._new_content_type = 'content-type-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_called_with(
            Bucket='foo',
            ContentType='content-type-bar',
            CopySource='foo/bar',
            Key='bar',
            Metadata={
                'meta-foo': 'meta-bar'
            },
            MetadataDirective='REPLACE'
        )

    def test_cache_control_unchanged(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'CacheControl': 'cache-control-bar',
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[],  key='bar')
        o_h._new_cache_control = 'cache-control-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_not_called()

    def test_content_type_unchanged(self, get_client):
        client = mock.MagicMock()
        get_client.return_value = client
        client.head_object = mock.MagicMock(return_value={
            'ContentType': 'content-type-bar',
            'Metadata': {
                'meta-foo': 'meta-bar'
            }
        })

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar')
        o_h._new_content_type = 'content-type-bar'  # pylint: disable=protected-access
        o_h._apply_changes()  # pylint: disable=protected-access

        client.copy_object.assert_not_called()


class QueueChangeTestCase(unittest.TestCase):
    def test_cache_control(self):
        o_h = ObjectHeaderizer(bucket='foo',
                               dry_run=True,
                               header_rules=[],
                               key='bar')

        o_h._queue_change(header='Cache-Control',  # pylint: disable=protected-access
                          value='foo')
        self.assertEqual(o_h._new_cache_control,  # pylint: disable=protected-access
                         'foo')

    def test_content_type(self):
        o_h = ObjectHeaderizer(bucket='foo',
                               dry_run=True,
                               header_rules=[],
                               key='bar')

        o_h._queue_change(header='Content-Type',  # pylint: disable=protected-access
                          value='foo')
        self.assertEqual(o_h._new_content_type,  # pylint: disable=protected-access
                         'foo')


@mock.patch.object(ObjectHeaderizer, '_apply_changes')
@mock.patch.object(ObjectHeaderizer, '_queue_changes')
class UpdateTestCase(unittest.TestCase):
    """ Tests for the "update" method. """

    def act(self):

        rules = [
            {
                'header': 'Cache-Control'
            }, {
                'header': 'Content-Type'
            }
        ]

        o_h = ObjectHeaderizer(bucket='foo', header_rules=rules, key='bar')
        o_h.update()

    def test_invokes_queue_changes_for_rule(self,
                                            queue_changes,
                                            apply_changes):  # pylint: disable=unused-argument
        """
        Asserts that the "apply_header_rule" method is invoked for every rule.
        """
        self.act()
        queue_changes.assert_has_calls(
            [
                mock.call(header_rule={
                    'header': 'Cache-Control'
                }),
                mock.call(header_rule={
                    'header': 'Content-Type'
                })
            ]
        )

    def test_invokes_apply_changes(self,
                                   queue_changes_for_rule,  # pylint: disable=unused-argument
                                   apply_changes):
        """
        Asserts that the "_apply_changes" method is invoked.
        """
        self.act()
        apply_changes.assert_called()


@mock.patch.object(ObjectHeaderizer, '_queue_change')
class ApplyHeaderRuleTestCase(unittest.TestCase):
    """ Tests for the "apply_header_rule" method. """

    def test_applies_explicit_rule(self, queue_change):
        """ Assert that an explicit rule is applied. """

        header_rule = {
            'header': 'Cache-Control',
            'when': [
                {
                    'extension': '.jpg',
                    'then': 'explicit-value'
                }
            ],
            'else': 'catch-all-value'
        }

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar.jpg')
        o_h._queue_changes(  # pylint: disable=protected-access
            header_rule=header_rule)

        queue_change.assert_has_calls(
            [
                mock.call(header='Cache-Control', value='explicit-value')
            ]
        )

    def test_applies_catch_all_rule(self, queue_change):
        """ Assert that a catch-all rule is applied. """

        header_rule = {
            'header': 'Cache-Control',
            'when': [
                {
                    'extension': '.jpg',
                    'then': 'explicit-value'
                }
            ],
            'else': 'catch-all-value'
        }

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar.html')

        o_h._queue_changes(  # pylint: disable=protected-access
            header_rule=header_rule)

        queue_change.assert_has_calls(
            [
                mock.call(header='Cache-Control', value='catch-all-value')
            ]
        )

    def test_applies_no_catch_all_rule(self, queue_change):
        """ Assert that no catch-all rule is applied. """

        rule = {
            'header': 'Cache-Control',
            'when': [
                {
                    'extension': '.jpg',
                    'then': 'explicit-value'
                }
            ]
        }

        o_h = ObjectHeaderizer(bucket='foo', header_rules=[], key='bar.html')

        o_h._queue_changes(  # pylint: disable=protected-access
            header_rule=rule)

        queue_change.assert_not_called()
