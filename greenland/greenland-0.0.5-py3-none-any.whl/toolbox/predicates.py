#
#   Greenland -- a Python based scripting environment.
#   Copyright (C) 2015-2017  M E Leypold.
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation; either version 2 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
#   02110-1301 USA.

"""
Module `toolbox.predicates` provides a ways to compose predicates in a
pointfree_ fashion.

.. TBD test: extract (sep) example for predicate creation,
       predicate composition (both ways), extra examples

.. TBD test: short circuit evaluation
.. TBD test: AND/OR/NOT can be used on any callable returning bool

.. _pointfree: https://en.wikipedia.org/wiki/Tacit_programming

.. _predicate_composition-operator-table:

.. tabularcolumns:: |L|L|L|L|L|

================  =========== =================== ===============   ===================
Operation         as Operator Example             As Identifier     Example
================  =========== =================== ===============   ===================
logical and       :samp:`&`   :samp:`p & q`       :samp:`<<AND>>`   :samp:`p <<AND>> q`
logical or        :samp:`|`   :samp:`p | q`       :samp:`<<OR>>`    :samp:`p <<OR>>`
logical negation  :samp:`~`   :samp:`~p`          :samp:`NOT`       :samp:`NOT(p)`
================  =========== =================== ===============   ===================

A predicate here is a *callable* that takes one argument (obviously
this argument could also be a tuple or a list, so, in a sense, this is
not a restriction).

.. For more information see: predicates.rst
"""

from abc import abstractmethod
from infix import shift_infix as infix


class Predicate (object):

    """
    Subclass this class to define a family of parametrized predicates
    (like: greater(10), greater(15)). Instances of the subclass are
    predicates, that means callables with return type bool and overloaded
    operators :code:`&`, :code:`|` and :code:`~` for composition.

    To define new predicate family one needs to derive from
    :py:class:`Predicate` and implement :py:meth:`__init__` and
    :py:meth:`__call__`.

    .. automethod:: __init__

    .. automethod:: __call__

    """

    @abstractmethod
    def __call__(self, subject):
        """Overwrite this method to implement the application of predicate to `subject`."""

    @abstractmethod
    def __init__(self, *pargs, **kwargs):
        """Overwrite this method to capture parameters at predicate construction."""

    def __or__(self, term2):
        return Disjunction(self, term2)

    def __and__(self, term2):
        return Conjunction(self, term2)

    def __invert__(self):
        return Negation(self)

    def __ror__(self, term1):
        return Disjunction(term1, self)

    def __rand__(self, term1):
        return Conjunction(term1, self)


class Conjunction (Predicate):

    def __init__(self, term1, term2):
        self.term1 = term1
        self.term2 = term2

    def __call__(self, subject):
        if self.term1(subject):
            return self.term2(subject)
        else:
            return False


class Disjunction (Predicate):

    def __init__(self, term1, term2):
        self.term1 = term1
        self.term2 = term2

    def __call__(self, subject):
        if self.term1(subject):
            return True
        else:
            return self.term2(subject)


class Negation (Predicate):
    def __init__(self, term):
        self.term = term

    def __call__(self, subject):
        return not(self.term(subject))


class PredicateFromFunction (Predicate):

    def __init__(self, pred):
        self.pred = pred

    def __call__(self, subject):
        return self.pred(subject)


def predicate(pred):

    """
    Decorator or function to turn a callable into a predicate.

    Example
    -------

    .. literalinclude:: test/predicates.py
       :start-after:    EXAMPLE:greater
       :end-before:     END
       :linenos:
       :dedent:      4
    """

    return PredicateFromFunction(pred)


@infix
def AND(a, b):

    """Standalone composition operator <<AND>>"""

    return Conjunction(a, b)


@infix
def OR(a, b):

    """Standalone composition operator <<OR>>"""

    return Disjunction(a, b)


def NOT(a):

    """Standalone negation operator 'NOT'"""

    return Negation(a)
