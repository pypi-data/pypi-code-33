# -*- coding: utf-8 -*-
 
from sql.operators import BinaryOperator
from sql import Flavor
from sql.functions import Function

__all__ = ['FuzzyEqal', 'Ascii', 'Concat2', 'RPad', 'Lower', 'ArrayAgg', 
            'Replace', 'AnyInArray', 'ReplaceRegexp']


class FuzzyEqal(BinaryOperator):
    """ read: https://www.rdegges.com/2013/easy-fuzzy-text-searching-with-postgresql/
        run 'CREATE EXTENSION pg_trgm;' to enable fuzzymatch in postgresql
    """
    __slots__ = ()

    @property
    def _operator(self):
        # '%' must be escaped with format paramstyle
        if Flavor.get().paramstyle == 'format':
            return '%%'
        else:
            return '%'


class Ascii(Function):
    """ASCII code of the first character of the argument. Syntax: Ascii(<string>), Result: int"""
    __slots__ = ()
    _function = 'ASCII'


class Concat2(Function):
    """Concatenate the text representations of all the arguments. NULL arguments are ignored.
        Syntax: Concat2(<string>, <string> [, ...]), Result: text
    """
    __slots__ = ()
    _function = 'CONCAT'


class RPad(Function):
    """Fill up the 'string' to 'length' by appending the characters 'fill' (a space by default). 
    If the string is already longer than 'length' then it is truncated.
    Syntay: RPad(<string>, <length>[, <fill>]), Result: text"""
    __slots__ = ()
    _function = 'RPAD'


class Lower(Function):
    """Convert string to lower case. Syntax: Lower(<string>), Result: text"""
    __slots__ = ()
    _function = 'LOWER'


class ArrayAgg(Function):
    """input values, including nulls, concatenated into an array.
    Syntax (in a group-by-clause): ArrayAgg(<column>), Result: Array"""
    __slots__ = ()
    _function = 'ARRAY_AGG'


class ReplaceRegexp(Function):
    """Replace substring(s) matching a POSIX regular expression. See Section https://www.postgresql.org/docs/9.4/static/functions-matching.html#FUNCTIONS-POSIX-REGEXP for more information.
       Syntax: ReplaceRegexp(text, pattern, replacement)"""
    __slots__ = ()
    _function = 'REGEXP_REPLACE'
    
class Replace(Function):
    """Replace all occurrences in 'string' of substring 'from' with substring 'to'. 
    Syntax: Replace(<string>, <from>, <to>), Result: text"""
    __slots__ = ()
    _function = 'REPLACE'


class AnyInArray(Function):
    """Test if a value exists in an array.
    https://www.postgresql.org/docs/9.5/static/functions-comparisons.html,
    Syntax: (<int> == AnyInArray(<array of int>)), Result: Boolean
    """
    __slots__ = ()
    _function = 'ANY'
  
    def __str__(self):
        Mapping = Flavor.get().function_mapping.get(self.__class__)
        if Mapping:
            return str(Mapping(*self.args))
        return self._function + '(' + ', '.join(
            map(self._format, self.args)) + '::int[])'
  
class SplitPart(Function):
    """Split 'string' on 'delimiter' and return the given 'field' (counting from one).
    Syntax: SplitPart(<string>, <delimiter>, <field>), Result: text"""
    __slots__ = ()
    _function = 'SPLIT_PART'
