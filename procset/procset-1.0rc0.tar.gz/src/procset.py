# -*- coding: utf-8 -*-

# Copyright © 2017—2019
# Contributed by Raphaël Bleuse <cs@research.bleuse.net>
#
# This file is part of procset.py, a pure python module to manage sets of
# closed intervals.
#
#   procset.py is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License version 3 only
#   as published by the Free Software Foundation.
#
#   procset.py is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License version 3 for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License version 3 along with this program.  If not, see
#   <https://www.gnu.org/licenses/>.

"""
Toolkit to manage sets of closed intervals.

This implementation requires intervals bounds to be non-negative integers. This
design choice has been made as procset aims at managing resources for
scheduling. Hence, the manipulated intervals can be represented as indexes.
"""

import operator as _operator


class ProcInt(tuple):
    """A ProcInt is a closed interval of non-negative integers."""

    __slots__ = ()

    __NEW_SENTINEL = object()  # sentinel for optional sup

    def __new__(cls, inf, sup=__NEW_SENTINEL):
        """Create new instance of ProcInt(inf, sup)."""
        if not isinstance(inf, int):
            raise TypeError('{}() argument inf must be int'.format(cls.__name__))
        if sup is cls.__NEW_SENTINEL:
            sup = inf
        if not isinstance(sup, int):
            raise TypeError('{}() argument sup must be int'.format(cls.__name__))
        if inf > sup:
            raise ValueError('Invalid interval bounds')
        if inf < 0:
            raise ValueError('Invalid negative bound(s)')
        return tuple.__new__(cls, (inf, sup))

    def __getnewargs__(self):
        return tuple(self)

    def __repr__(self):
        """Return a nicely formatted representation string."""
        return '{}(inf={!r}, sup={!r})'.format(type(self).__name__, *self)

    def __str__(self):
        return format(self)

    def __format__(self, format_spec):
        if self.inf == self.sup:
            return str(self.inf)
        else:
            if len(format_spec) > 1:
                raise ValueError('Invalid format specifier')
            insep = format_spec or '-'
            return insep.join(map(str, self))

    def __len__(self):
        return self.sup - self.inf + 1

    def __contains__(self, item):
        return self.inf <= item <= self.sup

    inf = property(_operator.itemgetter(0), doc='Alias for field number 0')

    sup = property(_operator.itemgetter(1), doc='Alias for field number 1')


class _Sentinel:
    """Helper class whose instances are greater than any object."""

    __slots__ = ()

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return False

    __le__ = __eq__

    def __gt__(self, other):
        return True

    __ge__ = __gt__


class ProcSet:
    """
    A ProcSet is a set of non-overlapping ProcInt.

    The current implementation uses a sorted list of ProcSet to store the
    ProcInt.
    """

    __slots__ = ('_itvs', )

    def __init__(self, *intervals):
        """
        Initialize a ProcSet.

        A ProcSet can be initialized with either nothing (empty set), any
        number of non-negative int, any number of ProcInt compatible objects
        (iterable of exactly 2 int), any number of ProcSet, or any combination
        of such objects.

        *New in version XXX:* __init__ accepts ProcSet objects.

        There are no restrictions on the domains of the intervals in the
        constructor: they may overlap.

        The resulting ProcSet is the union of all intervals in the constructor.

        Examples:
            ProcSet()  # empty set
            ProcSet(1)
            ProcSet(ProcInt(0, 1))
            ProcSet(ProcInt(0, 1), ProcInt(2, 3))
            ProcSet((0, 1), [2, 3])  # identical to previous call
            ProcSet(ProcInt(0, 1), *[0, 3])  # mixing ProcInt and lists
        """
        self._itvs = []  # list of disjoint intervals, in increasing order
        for new_itvs in map(self._as_itvs, intervals):
            self._itvs = list(self._merge(self._itvs, new_itvs, _operator.or_))

    @classmethod
    def from_str(cls, string, insep="-", outsep=" "):
        """Parse a string interval set representation into a ProcSet."""
        if not isinstance(string, str):
            raise TypeError(
                'from_str() argument 2 must be str, not {}'.format(type(string).__name__)
            )

        # empty string is parsed as empty ProcSet
        if not string:
            return cls()

        try:
            raw_bounds = (
                map(int, itv.split(sep=insep, maxsplit=1))
                for itv in string.split(sep=outsep)
            )
            intervals = (ProcInt(*bounds) for bounds in raw_bounds)
            return cls(*intervals)
        except ValueError:
            raise ValueError(
                'Invalid interval format, parsed string is: \'{}\''.format(string)
            ) from None

    def __str__(self):
        return format(self)

    def __format__(self, format_spec):
        if format_spec:
            try:
                insep, outsep = format_spec
            except ValueError:
                raise ValueError('Invalid format specifier') from None
        else:
            insep, outsep = '- '

        return outsep.join(format(itv, insep) for itv in self._itvs)

    def __repr__(self):
        compact = lambda itv: str(tuple(itv)) if len(itv) > 1 else str(itv.inf)
        args = (compact(itv) for itv in self._itvs)
        return '{}({})'.format(type(self).__name__, ', '.join(args))

    def __iter__(self):
        """Iterate through the processors in self by increasing order."""
        # as self._itvs is sorted by increasing order, we can directly yield
        for itv in self._itvs:
            yield from range(itv.inf, itv.sup + 1)

    def __reversed__(self):
        """Iterate through the processors in self by decreasing order."""
        # as self._itvs is sorted in increasing order, we yield from the
        # reversed iterator
        for itv in reversed(self._itvs):
            yield from reversed(range(itv.inf, itv.sup + 1))

    def __contains__(self, item):
        """Check if item is in self."""
        if self._itvs:
            low, high = 0, len(self._itvs)
            while low < high:
                mid = (low + high) // 2
                if item in self._itvs[mid]:
                    return True
                elif item < self._itvs[mid].inf:
                    high = mid
                else:
                    low = mid + 1
        return False

    def __eq__(self, other):
        # pylint: disable=protected-access
        return self._itvs == other._itvs

    def __bool__(self):
        return bool(self._itvs)

    def __len__(self):
        """Return the number of processors."""
        return sum(len(itv) for itv in self._itvs)

    def count(self):
        """Return the number of disjoint processors' intervals."""
        return len(self._itvs)

    def iscontiguous(self):
        """Return True if the processors form a single contiguous set."""
        return self.count() <= 1

    def isdisjoint(self, other):
        """Return True if self has no processor in common with other."""
        if not isinstance(other, type(self)):
            try:
                other = type(self)(*other)
            except TypeError:
                return NotImplemented

        # A naive implementation would test the truthiness of the intersection
        # set.  However, one does not care about the intersection set.  It is
        # sufficient to test if the generator returned by _merge is empty.
        _sentinel = object()
        # pylint: disable=protected-access
        _first = next(self._merge(self._itvs, other._itvs, _operator.and_), _sentinel)
        return _first is _sentinel

    def _issubset(self, other):
        return self & other == self

    def issubset(self, other):
        """Test whether every element in self is in other."""
        if not isinstance(other, type(self)):
            try:
                other = type(self)(*other)
            except TypeError:
                return NotImplemented
        return self._issubset(other)

    def __le__(self, other):
        """Test whether every element in self is in other."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._issubset(other)

    def __lt__(self, other):
        """
        Test whether self is a proper subset of other, that is
        self <= other and self != other.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._issubset(other) and self != other

    def issuperset(self, other):
        """Test whether every element in other is in self."""
        if not isinstance(other, type(self)):
            try:
                other = type(self)(*other)
            except TypeError:
                return NotImplemented
        # pylint: disable=protected-access
        return other._issubset(self)

    def __ge__(self, other):
        """Test whether every element in other is in self."""
        if not isinstance(other, type(self)):
            return NotImplemented
        # pylint: disable=protected-access
        return other._issubset(self)

    def __gt__(self, other):
        """
        Test whether self is a proper superset of other, that is
        self >= other and self != other.
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        # pylint: disable=protected-access
        return other._issubset(self) and self != other

    @staticmethod
    def _flatten(itvs):
        """Generate the (flat) list of interval bounds contained in itvs."""
        for itv in itvs:
            # use inf as is
            yield False, itv.inf
            # convert sup, as merging operations are made with half-open
            # intervals
            yield True, itv.sup + 1

    @classmethod
    def _merge_core(cls, left_itvs, right_itvs, keeppredicate):
        """
        Generate the (flat) list of interval bounds of the requested merge.

        The implementation is inspired by https://stackoverflow.com/a/20062829.
        """
        endbound = False
        sentinel = _Sentinel()

        # pylint: disable=protected-access
        lflat = cls._flatten(left_itvs)
        rflat = cls._flatten(right_itvs)
        lend, lhead = next(lflat, (False, sentinel))
        rend, rhead = next(rflat, (False, sentinel))

        head = min(lhead, rhead)
        while head < sentinel:
            inleft = (head < lhead) == lend
            inright = (head < rhead) == rend
            keep = keeppredicate(inleft, inright)

            if keep ^ endbound:
                endbound = not endbound
                yield head
            if head == lhead:
                lend, lhead = next(lflat, (False, sentinel))
            if head == rhead:
                rend, rhead = next(rflat, (False, sentinel))

            head = min(lhead, rhead)

    @classmethod
    def _merge(cls, left_itvs, right_itvs, keeppredicate):
        """
        Generate the ProcInt list of the requested merge.

        The returned iterator is supposed to be assigned to the _itvs attribute
        of the result ProcSet.
        See the difference(), intersection(), symmetric_difference(), and
        union() methods for an usage example.
        """
        flat_merge = cls._merge_core(left_itvs, right_itvs, keeppredicate)

        # Note that we are feeding the same iterable twice to zip.
        # The iterated bounds are hence grouped by pairs (lower and upper
        # bounds of the intervals).
        # As zip() stops on the shortest iterable, it won't consider the
        # optional terminating sentinel (the sentinel would be the last
        # element, and would have an odd index).
        for inf, sup in zip(flat_merge, flat_merge):
            yield ProcInt(inf, sup - 1)  # convert back to closed intervals

    def union(self, *others):
        """Return a new ProcSet with elements from self and all others."""
        result = self.copy()
        for other in map(self._as_itvs, others):
            # pylint: disable=protected-access
            result._itvs = list(result._merge(result._itvs, other, _operator.or_))
        return result

    def __or__(self, other):
        """Return a new ProcSet with the intervals from self and other."""
        if not isinstance(other, type(self)):
            return NotImplemented

        # We directly assign result._itvs as self._merge(…) returns a valid
        # _itvs list. This is the same as ProcSet(*self._merge(…)), minus the
        # input validation step.
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = list(self._merge(self._itvs, other._itvs, _operator.or_))
        return result

    def intersection(self, *others):
        """Return a new ProcSet with elements common to self and all others."""
        result = self.copy()
        for other in map(self._as_itvs, others):
            # pylint: disable=protected-access
            result._itvs = list(result._merge(result._itvs, other, _operator.and_))
        return result

    def __and__(self, other):
        """Return a new ProcSet with the intervals common to self and other."""
        if not isinstance(other, type(self)):
            return NotImplemented

        # We directly assign result._itvs as self._merge(…) returns a valid
        # _itvs list. This is the same as ProcSet(*self._merge(…)), minus the
        # input validation step.
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = list(self._merge(self._itvs, other._itvs, _operator.and_))
        return result

    @staticmethod
    def _difference_operator(inleft, inright):
        return inleft and not inright

    def difference(self, *others):
        """
        Return a new ProcSet with elements in self that are not in the others.
        """
        result = self.copy()
        for other in map(self._as_itvs, others):
            # pylint: disable=protected-access
            result._itvs = list(result._merge(result._itvs, other, self._difference_operator))
        return result

    def __sub__(self, other):
        """
        Return a new ProcSet with the intervals in self that are not in other.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # We directly assign result._itvs as self._merge(…) returns a valid
        # _itvs list. This is the same as ProcSet(*self._merge(…)), minus the
        # input validation step.
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = list(
            self._merge(self._itvs, other._itvs, self._difference_operator)
        )
        return result

    def symmetric_difference(self, other):
        """
        Return a new ProcSet with elements in either self or other, but not
        both.
        """
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = list(result._merge(self._itvs, self._as_itvs(other), _operator.xor))
        return result

    def __xor__(self, other):
        """
        Return a new ProcSet with the intervals in either self or other, but
        not both.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # We directly assign result._itvs as self._merge(…) returns a valid
        # _itvs list. This is the same as ProcSet(*self._merge(…)), minus the
        # input validation step.
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = list(self._merge(self._itvs, other._itvs, _operator.xor))
        return result

    def copy(self):
        """Return a shallow copy of self."""
        # We directly assign result._itvs as self._itvs is a valid list.  Note
        # that a ProcSet is nothing more than a container with some extra
        # methods, and a given structure.  As the current implementation relies
        # on the _itvs list, copying a ProcSet is the same as copying the _itvs
        # list.  Hence, we need to ensure a new _itvs list is created (and not
        # just a reference to self._itvs).  As _itvs is a list of ProcInt, a
        # shallow copy is the same as a deep copy.
        result = type(self)()
        # pylint: disable=protected-access
        result._itvs = self._itvs.copy()
        return result

    __copy__ = copy  # ensure compatibility with standard module copy

    def __deepcopy__(self, memo):
        # Optimized version of __deepcopy__ for ProcSet.
        # /!\ This optimization is implementation specific /!\
        # The classic __deepcopy__ implementation can be bypassed because a
        # ProcInt is an immutable structure: there is no need to use the
        # generic and complex implementation of deepcopy for tuples that may
        # contain mutables.
        return self.copy()

    def update(self, *others):
        """Update the ProcSet, adding elements from all others."""
        for other in map(self._as_itvs, others):
            self._itvs = list(self._merge(self._itvs, other, _operator.or_))
        return self

    insert = update  # backward compatibility alias

    def __ior__(self, other):
        """Update the ProcSet, adding the intervals from other."""
        if not isinstance(other, type(self)):
            return NotImplemented

        # pylint: disable=protected-access
        self._itvs = list(self._merge(self._itvs, other._itvs, _operator.or_))
        return self

    def intersection_update(self, *others):
        """
        Update the ProcSet, keeping only elements found in self and all others.
        """
        for other in map(self._as_itvs, others):
            self._itvs = list(self._merge(self._itvs, other, _operator.and_))
        return self

    def __iand__(self, other):
        """
        Update the ProcSet, keeping only the intervals found in self and other.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # pylint: disable=protected-access
        self._itvs = list(self._merge(self._itvs, other._itvs, _operator.and_))
        return self

    def difference_update(self, *others):
        """Update the ProcSet, removing elements found in others."""
        for other in map(self._as_itvs, others):
            self._itvs = list(self._merge(self._itvs, other, self._difference_operator))
        return self

    discard = difference_update  # convenience alias

    def __isub__(self, other):
        """Update the ProcSet, removing the intervals found in other."""
        if not isinstance(other, type(self)):
            return NotImplemented

        # pylint: disable=protected-access
        self._itvs = list(self._merge(self._itvs, other._itvs, self._difference_operator))
        return self

    def symmetric_difference_update(self, other):
        """
        Update the ProcSet, keeping only elements found in either self or
        other, but not in both.
        """
        self._itvs = list(self._merge(self._itvs, self._as_itvs(other), _operator.xor))
        return self

    def __ixor__(self, other):
        """
        Update the ProcSet, keeping only the intervals found in either self or
        other, but not in both.
        """
        if not isinstance(other, type(self)):
            return NotImplemented

        # pylint: disable=protected-access
        self._itvs = list(self._merge(self._itvs, other._itvs, _operator.xor))
        return self

    def clear(self):
        self._itvs = []

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError(
                '{} indices must be integers, not {}'.format(
                    type(self).__name__,
                    type(index).__name__
                )
            )
        if index >= 0:
            for itv in self._itvs:
                if index < len(itv):
                    return itv.inf + index
                else:
                    index -= len(itv)
        else:
            for itv in reversed(self._itvs):
                if index >= -len(itv):
                    return itv.sup + 1 + index
                else:
                    index += len(itv)
        raise IndexError('{} index out of range'.format(type(self).__name__))

    # we do not define __setitem__ as it makes no sense to modify a processor

    def __delitem__(self, index):
        raise NotImplementedError

    def aggregate(self):
        """
        Return the ProcSet that is the convex hull of self.

        If self is empty, its convex hull is the empty ProcSet.
        If self is not empty, its convex hull is the ProcSet with the smallest
        interval containing all intervals from self.
        """
        if self._itvs:
            return type(self)(ProcInt(self.min, self.max))
        else:
            return type(self)()

    def intervals(self):
        """Return an iterator on the intervals of self in increasing order."""
        return iter(self._itvs)

    @property
    def min(self):
        """The first processor in self (in increasing order)."""
        try:
            return self._itvs[0].inf
        except IndexError:
            raise ValueError('Empty ProcSet') from None

    @property
    def max(self):
        """The last processor in self (in increasing order)."""
        try:
            return self._itvs[-1].sup
        except IndexError:
            raise ValueError('Empty ProcSet') from None

    @staticmethod
    def _as_procint(elem):
        """Yield elem as a ProcInt."""
        try:  # ProcInt-compatible (iterable of exactly 2 int)
            inf, sup = elem
        except ValueError:
            raise TypeError(
                'Incompatible iterable, expected an iterable of exactly 2 int'
            ) from None
        except TypeError:  # single point (non-negative int)
            inf, sup = elem, elem

        yield ProcInt(inf, sup)

    @classmethod
    def _as_itvs(cls, other):
        """Iterate over other as an _itvs list."""
        if isinstance(other, cls):
            # pylint: disable=protected-access
            yield from other._itvs
        else:
            yield from cls._as_procint(other)
