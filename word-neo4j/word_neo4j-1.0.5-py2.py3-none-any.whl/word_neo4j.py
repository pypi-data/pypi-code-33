# -*- coding: utf-8 -*-
"""Word Neo4j.

This module contains classes for creating the word components of Neo4j Cypher
queries.

Todo:
    * Build pattern module that uses these words to build more advanced
    functionality.
    * Decide if we want to enforce convention (currently forcing keywords to
    be all caps and variable names to lower snake with leading underscore).
    * Remove logging.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
# import logging.config
import re

import word_neo4j.settings_accessor  # pylint: disable=import-error


_SETTINGS = word_neo4j.settings_accessor.SettingsAccessor()
# if _SETTINGS.logging_config:
#     logging.config.dictConfig(_SETTINGS.logging_config)
# _LOGGER = logging.getLogger(__name__)
# _LOGGER.setLevel(logging.INFO)


def to_lower_snake_case(name):
    """To lower snake case.

    Converts a string from CamelCase to snake_case.

    Args:
        name (str): String to convert.

    Returns:
        str: Converted string.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484/

    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Keyword:
    """Keywords makes Neo4j Cypher keyword strings.

    A keyword is a reserved word for specific actions in a query (MATCH,
    WHERE, WITH etc.).

    Attributes:
        word (str): Keyword string.

    """

    def __init__(self, value):
        """Initialize Keyword object.

        That's it.

        Args:
            value (str): Input string.

        """
        self._word = value

    @property
    def word(self):
        """str: Capitalizes."""
        return self._word.upper()


class Node:
    """Node is for making Neo4j nodes.

    A node is
    Case sensitive.

    Attributes:
        word (str): String to be used in Cypher.

    """

    def __init__(self, value, variable=True, variable_name=None):
        """Initialize Node object.

        Variable indicates if should provide node with a variable name.
        Variable name is the name of variable to provide.

        If a variable name is provided, a variable will be created unless
        variable is explicitly set to False.

        Args:
            value (str|None): Input string.
            variable (bool): Variable name to give node.
            variable_name (str):

        """
        self._value = value
        self._variable = variable
        self._variable_name = variable_name
        # _LOGGER.debug(str(self))

    def __str__(self):
        return """{}('{}')""".format(
            self.__class__.__name__,
            self._value
        )

    @property
    def word(self):
        """str: Creates node."""
        if self._value:
            if self._variable:
                if self._variable_name:
                    variable_name = self._variable_name
                else:
                    variable_name = '_' + to_lower_snake_case(self._value)
                out = '({}:{})'.format(variable_name, self._value)
            else:
                out = '(:{})'.format(self._value)
        else:
            out = '()'
        return out


class Relationship:
    """Relationship is for making Neo4j relationships.

    A relationship is a way of connecting nodes.
    Case sensitive.

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

    def __str__(self):
        return """{}({}, direction='{}')""".format(
            self.__class__.__name__,
            self._value,
            self._direction,
        )

    @property
    def word(self):
        """str: Creates relationship word."""
        # _LOGGER.debug(str(self))
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
    Case sensitive.

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
