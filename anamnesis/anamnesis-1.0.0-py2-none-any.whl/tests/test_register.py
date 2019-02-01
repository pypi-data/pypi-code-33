#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

import unittest


class Foo():
    pass


class Foo2():
    pass


class Foo3():
    hdf5_aliases = ['test.tdra.Foo2']


class Foo4():
    pass


class Foo5():
    hdf5_aliases = ['test.toa.oldname']


# Remember to use different names for each of these tests as otherwise the
# references persist between tests....


class TestRegister(unittest.TestCase):
    def test_register(self):
        """Test the ClassHandler code can register and retrieve a class using
        an explicit name"""

        from ..register import register_class, find_class

        register_class(Foo, 'test.tr_foo')

        res = find_class('test.tr_foo')

        assert (res == Foo)

    def test_register_implicit(self):
        """Test the ClassHandler code can register and retrieve a class
        automatically"""

        from ..register import register_class, find_class

        name = '.'.join([Foo.__module__, Foo.__name__])

        register_class(Foo)

        res = find_class(name)

        assert (res == Foo)

    def test_doubleregister(self):
        """Test the ClassHandler code doesn't allow double registration"""

        from ..register import register_class

        register_class(Foo, 'test.tdr_foo')

        self.assertRaises(Exception, register_class, Foo, 'test.tdr_foo')

    def test_doubleregisteralias(self):
        """Test that we handle not double registering aliases"""

        from ..register import register_class

        register_class(Foo2, 'test.tdra.Foo2')

        self.assertRaises(Exception, register_class, Foo3,
                          'test.tdra.foo3')

    def test_permitted_prefix(self):
        """Test that we handle permitted prefixes properly"""
        from ..register import ClassRegister

        c = ClassRegister()

        assert(c.check_permitted_prefix('testpp') is False)

        c.add_permitted_prefix('testpp')

        assert(c.check_permitted_prefix('testpp') is True)

    def test_not_there(self):
        """Test what happens when a class doesn't exist"""
        from ..register import find_class

        ret = find_class('anamnesis.doesnotexist.Class')

        assert(ret is None)

    def test_alias(self):
        """Test alias registration"""
        from ..register import find_class, register_class

        assert(find_class('test.toa.oldname') is None)

        register_class(Foo5)

        assert(find_class('test.toa.oldname') is not None)

    def test_hints(self):
        """Test that we handle class hints properly"""
        from ..register import ClassRegister, find_class, register_class

        c = ClassRegister()

        # We know that this should be registered
        expected = 'naf.meg.beamformeranalyses.NAI'
        tmp = c.check_hint('naf.meg.beamformers.NAI')
        assert(expected == tmp)

        # We know that this shouldn't be registered
        assert(c.check_hint('testtt.th.th') is None)

        # Now register it and check again
        expected = 'testtt.th.th2'
        c.add_hint('testtt.th.th', 'testtt.th.th2')
        tmp = c.check_hint('testtt.th.th')
        assert(expected == tmp)

        # Register a class to match the target
        register_class(Foo4, 'testtt.th.th2')

        # And check we can load the class
        # We need to temporarily allow this prefix
        oldpp = c.permitted_prefixes[:]
        c.add_permitted_prefix('testtt')
        ret = find_class('testtt.th.th')
        assert(ret is not None)
        c.permitted_prefixes = oldpp

    def test_implicit_load(self):
        """Test whether we can find a module which hasn't been explicitly
        loaded"""
        from ..register import find_class

        ret = find_class('anamnesis.tests.class_example.AutoLoadTestCase')

        assert(ret is not None)

    def test_implicit_load_notallowed(self):
        """Test that we fail if we try to load an non-permitted module"""
        from ..register import find_class, ClassRegister

        # This requires hacking with the ClassRegister a bit
        c = ClassRegister()
        tmppp = c.permitted_prefixes[:]
        c.permitted_prefixes = []

        if 'anamnesis.tests.class_example.AutoLoadTestCase' in \
           c.class_register:
            c.class_register.pop(
                'anamnesis.tests.class_example.AutoLoadTestCase')

        ret = find_class('anamnesis.tests.class_example.AutoLoadTestCase')

        assert(ret is None)

        c.permitted_prefixes = tmppp
