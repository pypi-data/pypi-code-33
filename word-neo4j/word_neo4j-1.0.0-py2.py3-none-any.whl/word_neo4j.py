# -*- coding: utf-8 -*-
"""Word Neo4j.

This module contains classes for creating the word components of Neo4j Cypher
queries.

Todo:
    * Operation and Property classes

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import logging

import word_neo4j.send_notification  # pylint: disable=import-error
import word_neo4j.settings_accessor  # pylint: disable=import-error


_SETTINGS = word_neo4j.settings_accessor.SettingsAccessor()
_LOGGER = logging.getLogger(__name__)
_HANDLER = word_neo4j.send_notification.EmailHandler()
_LOGGER.addHandler(_HANDLER)
_LOGGER.setLevel(logging.WARNING)


class Identifier:
    """Identifier is for making Neo4j identifiers.

    An identifier is a reserved word in Neo4j Cypher
    (MATCH, WHERE, WITH, etc.).

    Attributes:
        word (str): String to be used in Cypher

    """
    def __init__(self, value):
        """Initialize Identifier object.

        That's it.

        Args:
            value (str): Input string.

        """
        self._word = value

    @property
    def word(self):
        """str: Capitalizes."""
        return self._word.upper()


class Alias:
    """Alias is for making Neo4j aliases.

    An alias is a temporary name given to a results set of nodes.

    Attributes:
        word (str): String to be used in Cypher.

    """

    def __init__(self, value):
        """Initialize Identifier object.

        That's it.

        Args:
            value (str): Input string.

        """
        self._word = value

    @property
    def word(self):
        """str: Prepends an '_'."""
        return '_' + self._word


class Label:
    """Label is for making Neo4j aliases.

    A label is a way of categorizing nodes.

    Attributes:
        word (str): String to be used in Cypher.

    """

    def __init__(self, value):
        """Initialize Label object.

        That's it.

        Args:
            value (str): Input string.

        """
        self._word = value

    @property
    def word(self):
        """str: Turns to upper camel case."""
        return ''.join(x for x in self._word.title() if not x == '_')


class Relationship:
    """Relationship is for making Neo4j relationships.

    A relationship is a way of connecting nodes.

    Attributes:
        word (str): String to be used in Cypher.

    """
    def __init__(self, value, direction='right'):
        """Initialize Label object.

        If value is None,
        Direction can be 'left' or 'right'. Defaults to 'right'.

        Args:
            value (str|None): Input string.
            direction (str): Indicates direction.

        """
        self._value = value
        self._direction = direction

    @property
    def word(self):
        """str: Turns to upper camel case."""
        if self._value:
            if self._direction == 'right':
                out = '-[:{}]->'.format(self._value.upper())
            else:  # Direction is left.
                out = '<-[:{}]-'.format(self._value.upper())
        else:
            if self._direction == 'right':
                out = '-[]->'
            else:  # Direction is left.
                out = '<-[]-'
        return out


class DynamicRelationship(Relationship):
    """Relationship is for making Neo4j relationships.

    A relationship is a way of connecting nodes.

    Attributes:
        word (str): String to be used in Cypher.

    """

    def __init__(self, label1, label2, database=None):
        """Initialize DynamicRelationship object.

        Direction can be 'left' or 'right'. Defaults to 'right'.

        Args:
            label1 (str): First label.
            label2 (str): Second label.
            database (Database): Database object.

        """
        self._label1 = label1
        self._label2 = label2
        self._database = database
        super().__init__(None)

    @property
    def word(self):
        value, direction = self._database.query(self._label1, self._label2)
        self._value = value
        self._direction = direction
        return super().word


if __name__ == '__main__':
    pass
