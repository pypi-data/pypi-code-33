#!/usr/bin/python
"""
    iters.py                         Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

NRG 12/01/10
"""
from __future__ import absolute_import

from builtins import next
import itertools
try:
    # Python 2
    imap         = itertools.imap
    ifilter      = itertools.ifilter
    ifilterfalse = itertools.ifilterfalse
except AttributeError:
    # Python 3
    imap         = map
    ifilter      = filter
    ifilterfalse = itertools.filterfalse

# Backwards compatibility: before we had a separate dicts module, we used to
# define subdict() and interdict() here in this module.
from .dicts import subdict, interdict

try:
    string_types = (str, unicode, bytes)
except NameError:
    # In Python 3, unicode isn't defined. To test whether something is a
    # string (or a byte string), we need only check (str, bytes).
    string_types = (str, bytes)

def iterable(obj):
    """Is obj a scalar or a sequence? This is very frequently asked by utility
    functions that might accept either: process either the single object I
    pass, or each item in this sequence.

    But the question has hidden subtleties. isinstance(obj, list) is obviously
    wrong -- what about tuples? Even isinstance(obj, (list, tuple)) isn't
    quite right. What about generators? What about 2.4 generator expressions?
    What about user-defined sequence classes?

    In exasperation we might simply write iter(obj). If it throws, obj is a
    scalar; otherwise it's a sequence. But that's not quite what we (usually)
    want either: you can iterate over the characters in a string...

    This function regards strings as scalars, but supports all other iterables
    as described above. Note that we test against string_types so that we notice
    either an ASCII string or a Unicode string.
    """
    if isinstance(obj, string_types):
        return False
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True

def sequence(obj):
    """Convenience function to support utility functions. If obj is already an
    iterable, return it unchanged; if it's a scalar, return a tuple containing
    that one entry. (We use iterable(), so we treat strings of both kinds as
    scalars.) This permits you to write:

    for item in sequence(obj): ...

    and accept scalars, sequences, generators, whatever.
    """
    if iterable(obj):
        return obj
    else:
        return (obj,)

def empty(iterable):
    """If you want to know whether a sequence is empty, it's common to ask
    whether len(sequence) == 0. But what if the sequence is a generator, and
    it may run indefinitely -- or infinitely?

    This function cheaply tests whether the passed iterable returns no items,
    or at least one item.
    """
    try:
        next(iter(iterable))
        return False
    except StopIteration:
        return True

try:
    # This seemingly pointless assignment in fact sets iters.any to be the
    # same as the builtin any() function. Old consumers might use iters.any().
    any = any
except NameError:
    # Python 2.4 or earlier
    def any(iterable):
        """True if any one bool(item) in the iterable is True. Equivalent to
        reduce(or, iterable) -- except that you can't write reduce(or, ...).
        """
        return not empty(ifilter(None, iterable))

try:
    # Defines iters.all()
    all = all
except NameError:
    # Python 2.4 or earlier
    def all(iterable):
        """True if every bool(item) in the iterable is True. Equivalent to
        reduce(and, iterable) -- except that you can't write reduce(and, ...).
        """
        return empty(ifilterfalse(None, iterable))

def interleave(*iterables):
    """Return the first item from the first iterable, then the first item from
    the second iterable, then the first item from the third iterable, and so
    on for all the iterables. Then return the second item from the first
    iterable, etc. Like itertools.imap(None) except that it returns individual
    items in sequence instead of returning tuples.
    """
    # In Python 2, itertools.imap(None) yields a sequence of tuples. Python
    # 3's map() doesn't support None, so we must pass a function that collects
    # arbitrary positional arguments into a single sequence. list() doesn't do
    # that; tuple() doesn't do that: each expects a single iterable argument.
    # But (lambda *args: args) does that: collect arbitrary arguments into a
    # tuple, then just return the tuple.
    # Flatten that sequence of tuples by passing each tuple as a distinct
    # argument to chain(). We don't even need to handle each item on its way by.
    return itertools.chain(*imap(lambda *args: args, *iterables))

def lastflag(iterable):
    """
    Return (item, is_last) pair for every item in the passed iterable, where
    is_last is a bool: True the very last one in iterable, False for every
    preceding one. This works even when the passed iterable is a generator, or
    any other sequence for which len(iterable) doesn't work.

    If iterable is empty, lastflag(iterable) likewise produces an empty
    sequence.
    """
    rest = iter(iterable)
    # Capture first item. If 'iterable' is completely empty, let StopIteration
    # propagate.
    old = next(rest)
    # loop through all the 'rest'
    for new in rest:
        # 'new' may or may not be the last item -- but since we're here in the
        # loop body, since 'new' exists, 'old' is definitely NOT last.
        yield old, False
        # save the new item for next iteration
        old = new
    # 'rest' is exhausted -- that means 'old' is in fact the last item
    yield old, True
