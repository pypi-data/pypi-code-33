"""
Utility functions to deal with string and class names.
"""

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2019, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

import re
from typing import Optional

indentation: int = 4


def namespace_name(fully_qualified_name: str) -> str:
    """
    Return the namespace name of a fully qualified class name.
    :param fully_qualified_name: The fully qualified name
    """
    tokens = fully_qualified_name.split('.')
    return '.'.join(tokens[:-1])


def class_name(fully_qualified_name: str) -> str:
    """
    Returns the class name of a fully qualified class name.

    :param fully_qualified_name: The fully qualified name
    """
    tokens = fully_qualified_name.split('.')
    return tokens[-1]


def to_snake_case(camel_str: str) -> str:
    """
    CamelCase str to snake_case

    :param camel_str: The str in input
    """
    capitalized_snake_str = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', capitalized_snake_str).lower()


def to_camel_case(snake_str: str, except_first: bool = True) -> str:
    """
    snake_case string to CamelCase

    :param snake_str: The input str
    :param except_first: does not capitalise the first letter
    """
    components = snake_str.split('_')
    if except_first:
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return components[0] + ''.join(x.title() for x in components[1:])
    return ''.join(x.title() for x in components)


def ind(i: int = 1) -> str:
    """
    Returns a number of spaces corresponding to the indentation level in input

    :param i: The indentation level
    """
    return ' ' * indentation * i


def j(*strings: Optional[str]) -> str:
    """
    Quick helper to join strings

    :param strings: The strings to join
    """
    return ''.join(s for s in strings if s)
