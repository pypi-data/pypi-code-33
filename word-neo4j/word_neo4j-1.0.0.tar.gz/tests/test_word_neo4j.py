#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `word_neo4j` package."""
import unittest.mock

from word_neo4j import word_neo4j


class TestIdentifier(unittest.TestCase):
    """Testing Identifier class."""
    def test_identifier(self):
        """Testing default identifier."""
        identifier = word_neo4j.Identifier('test')
        assert identifier.word == 'TEST'


class TestAlias(unittest.TestCase):
    """Testing Alias class."""
    def test_alias(self):
        """Testing default alias."""
        alias = word_neo4j.Alias('test')
        assert alias.word == '_test'


class TestLabel(unittest.TestCase):
    """Testing Label class."""
    def test_label(self):
        """Testing default label."""
        label = word_neo4j.Label('foo_bar')
        assert label.word == 'FooBar'


class TestRelationship(unittest.TestCase):
    """Testing Relationship class."""
    def test_relationship_default(self):
        """Testing default relationship."""
        relationship = word_neo4j.Relationship('foo_bar')
        assert relationship.word == '-[:FOO_BAR]->'

    def test_relationship_left(self):
        """Testing left relationship."""
        relationship = word_neo4j.Relationship('foo_bar', direction='left')
        assert relationship.word == '<-[:FOO_BAR]-'

    def test_empty_relationship(self):
        """Testing empty relationship."""
        relationship = word_neo4j.Relationship(None, direction='left')
        assert relationship.word == '<-[]-'

    def test_empty_right_relationship(self):
        """Testing empty right relationship."""
        relationship = word_neo4j.Relationship(None, direction='right')
        assert relationship.word == '-[]->'

    def test_dynamic_relationship(self):
        """Testing dynamic relationship."""
        database = unittest.mock.Mock()
        database.query = unittest.mock.Mock()
        database.query.return_value = ('FOO_BAR', 'left')
        relationship = word_neo4j.DynamicRelationship('foo', 'bar',
                                                      database=database)
        assert relationship.word == '<-[:FOO_BAR]-'
        database.query.assert_called_with('foo', 'bar')


if __name__ == '__main__':
    pass
