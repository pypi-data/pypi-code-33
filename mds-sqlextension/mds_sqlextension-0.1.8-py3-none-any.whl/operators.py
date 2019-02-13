# -*- coding: utf-8 -*-


from sql.operators import BinaryOperator

__all__ = ['RegexMatchNoCase', 'RegexMatchWithCase']


class RegexMatchNoCase(BinaryOperator):
    """ Match string with regular expression case insensitive, 
        Syntax: RegexMatchNoCase(<column>, <regular expression>),
        https://www.postgresql.org/docs/9.3/functions-matching.html#FUNCTIONS-POSIX-TABLE
    """
    __slots__ = ()
    _operator = '~*'


class RegexMatchWithCase(BinaryOperator):
    """ Match string with regular expression case sensitive, 
        Syntax: RegexMatchNoCase(<column>, <regular expression>),
        https://www.postgresql.org/docs/9.3/functions-matching.html#FUNCTIONS-POSIX-TABLE
    """
    __slots__ = ()
    _operator = '~'

