#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `word_neo4j` package."""
import unittest.mock

from word_neo4j import word_neo4j


class TestNode(unittest.TestCase):
    """Testing Node class."""
    def test_default(self):
        """Testing Node object creation with no kwargs."""
        node = word_neo4j.Node('FooBar')
        assert node.word == '(_foo_bar:FooBar)'

    def test_explicitly_no_variable(self):
        """Testing Node object creation with explicit variable=False."""
        node = word_neo4j.Node('FooBar', variable=False)
        assert node.word == '(:FooBar)'

    def test_explicitly_add_variable(self):
        """Testing Node object with variable=True'."""
        node = word_neo4j.Node('FooBar', variable=True)
        assert node.word == '(_foo_bar:FooBar)'

    def test_provided_variable_name(self):
        """Testing Node object with provided variable name."""
        node = word_neo4j.Node('FooBar', variable_name='baz')
        assert node.word == '(baz:FooBar)'

    def test_provided_variable_name_explicitly_no_variable(self):
        """Testing Node object

        With provided variable name and explicit variable=False.
        """
        node = word_neo4j.Node('FooBar', variable_name='baz', variable=False)
        assert node.word == '(:FooBar)'


class TestRelationship(unittest.TestCase):
    """Testing Relationship class."""
    def test_default(self):
        """Testing default relationship."""
        relationship = word_neo4j.Relationship('foo_bar')
        assert relationship.word == '-[:FOO_BAR]->'

    def test_left(self):
        """Testing left relationship."""
        relationship = word_neo4j.Relationship('foo_bar', direction='left')
        assert relationship.word == '<-[:FOO_BAR]-'

    def test_empty(self):
        """Testing empty relationship."""
        relationship = word_neo4j.Relationship(None, direction='left')
        assert relationship.word == '<-[]-'

    def test_empty_right(self):
        """Testing empty right relationship."""
        relationship = word_neo4j.Relationship(None, direction='right')
        assert relationship.word == '-[]->'


class TestDynamicRelationship(unittest.TestCase):
    def test_dynamic(self):
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
