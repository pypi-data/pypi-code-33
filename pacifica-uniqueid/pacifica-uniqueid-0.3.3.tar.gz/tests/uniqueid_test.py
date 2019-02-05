#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Index server unit and integration tests."""
from __future__ import print_function
import unittest
from peewee import SqliteDatabase
from pacifica.uniqueid.orm import UniqueIndex, update_index


class IndexServerUnitTests(unittest.TestCase):
    """Index server unit and integration tests."""

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the database with in memory sqlite."""
        self._db = SqliteDatabase('file:cachedb?mode=memory&cache=shared')
        for model in [UniqueIndex]:
            model.bind(self._db, bind_refs=False, bind_backrefs=False)
        self._db.connect()
        self._db.create_tables([UniqueIndex])

    def tearDown(self):
        """Tear down the database."""
        self._db.drop_tables([UniqueIndex])
        self._db.close()
        self._db = None
    # pylint: enable=invalid-name

    def test_index_update(self):
        """Test return and update of unique index."""
        test_object = UniqueIndex.create(idid='file', index=892)
        self.assertEqual(test_object.idid, 'file')

        index, index_range = update_index(10, 'file')
        self.assertEqual(index, 892)
        self.assertEqual(index_range, 10)

        index, index_range = update_index(10, 'file')
        self.assertEqual(index, 902)
        self.assertEqual(index_range, 10)

        index, index_range = update_index(10, 'new')
        self.assertEqual(index, 1)
        self.assertEqual(index_range, 10)

        index, index_range = update_index(10, 'new')
        self.assertEqual(index, 11)
        self.assertEqual(index_range, 10)

        index, index_range = update_index(None, 'new')
        self.assertEqual(index, -1)
        self.assertEqual(index_range, -1)

        index, index_range = update_index(2, None)
        self.assertEqual(index, -1)
        self.assertEqual(index_range, -1)

        index, index_range = update_index(-5, 'new')
        self.assertEqual(index, -1)
        self.assertEqual(index_range, -1)
