# -*- coding: utf-8 -*-
"""
    test.DummyClientFixture
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy client fixture
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from ..Dummy import Dummy

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

class DummyClientFixture:
    _client = None

    def __init__(self, client):
        self._client = client

    def test_crud_operations(self):
        # Create one dummy
        dummy1 = self._client.create(None, DUMMY1)

        assert None != dummy1
        assert None != dummy1['id']
        assert DUMMY1['key'] == dummy1['key']
        assert DUMMY1['content'] == dummy1['content']

        # Create another dummy
        dummy2 = self._client.create(None, DUMMY2)

        assert None != dummy2
        assert None != dummy2['id']
        assert DUMMY2['key'] == dummy2['key']
        assert DUMMY2['content'] == dummy2['content']

        # Get all dummies
        dummies = self._client.get_page_by_filter(None, None, None)
        assert None != dummies
        assert 2 == len(dummies.data)

        # Update the dummy
        dummy1['content'] = "Updated Content 1"
        dummy = self._client.update(None, dummy1)

        assert None != dummy
        assert dummy1['id'] == dummy['id']
        assert dummy1['key'] == dummy['key']
        assert "Updated Content 1" == dummy['content']

        # Delete the dummy
        self._client.delete_by_id(None, dummy1['id'])

        # Try to get deleted dummy
        dummy = self._client.get_one_by_id(None, dummy1['id'])
        assert None == dummy
