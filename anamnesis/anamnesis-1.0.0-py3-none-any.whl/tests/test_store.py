#!/usr/bin/python

"""Tests for abstract module"""
# vim: set expandtab ts=4 sw=4:

from ..test import AnamTestBase


class StoreTest(AnamTestBase):
    def test_init_store(self):
        """Check that we can initialise an empty Store object"""
        from ..store import Store
        s = Store()
        assert(isinstance(s, Store))

    def test_empty_store_equality(self):
        """Check that empty Store objects are equal"""
        from ..store import Store
        s = Store()
        t = Store()
        assert(s == t)

    def test_store_equality_1(self):
        """Check that used Store objects are equal if they contain the same
        item"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        t = Store()
        t.extra_data['foo'] = 1
        assert(s == t)

    def test_store_equality_2(self):
        """Check that used Store objects are equal if they contain the same
        multiple items"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        s.extra_data['bar'] = 'a'
        t = Store()
        t.extra_data['foo'] = 1
        t.extra_data['bar'] = 'a'
        assert(s == t)

    def test_store_inequality_1(self):
        """Check that used Store objects are unequal if they contain the same
        keys but different values"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        t = Store()
        t.extra_data['foo'] = 2
        assert(s != t)

    def test_store_inequality_2(self):
        """Check that used Store objects are unequal if they contain totally
        different keys"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        t = Store()
        t.extra_data['bar'] = 'a'
        assert(s != t)

    def test_store_inequality_3(self):
        """Check that used Store objects are unequal if they contain some of
        the same values and some different"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        s.extra_data['bar'] = 'a'
        t = Store()
        t.extra_data['foo'] = 1
        t.extra_data['bar'] = 'b'
        assert(s != t)

    def test_store_inequality_4(self):
        """Check that used Store objects are unequal if they contain some of
        the same things and the first has some extra keys"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        s.extra_data['bar'] = 'a'
        t = Store()
        t.extra_data['foo'] = 1
        assert(s != t)

    def test_store_inequality_5(self):
        """Check that used Store objects are unequal if they contain some of
        the same things and the second has some extra keys"""
        from ..store import Store
        s = Store()
        s.extra_data['foo'] = 1
        t = Store()
        t.extra_data['foo'] = 1
        t.extra_data['bar'] = 'a'
        assert(s != t)
