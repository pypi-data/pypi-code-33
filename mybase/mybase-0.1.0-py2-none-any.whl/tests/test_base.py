
# =========================================
#       IMPORTS
# --------------------------------------

import rootpath

rootpath.append()

from mybase.tests import helper

import mybase
import logging

from os import environ

environ['COLORS'] = 'true' # lower prio

environ['LOGGER_COLORS'] = 'false' # higher prio


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(mybase)

    def test_logger(self):
        base = mybase.Base()

        self.assertTrue(hasattr(base, 'name'))

        self.assertEqual(base.name, 'foo')

        class Foo(mybase.Base):
            pass

        foo = Foo()

        self.assertTrue(hasattr(foo, 'name'))

        self.assertEqual(foo.name, 'foo')

    def test_logger(self):
        base = mybase.Base()

        self.assertTrue(hasattr(base, 'logger'))
        self.assertIsInstance(base.logger, logging.Logger)

        class Foo(mybase.Base):
            def hello(self):
                self.logger.info('hello')

        foo = Foo()

        self.assertTrue(hasattr(foo, 'logger'))
        self.assertIsInstance(base.logger, object)
        self.assertTrue(hasattr(base.logger, 'log'))
        self.assertTrue(hasattr(base.logger, 'info'))
        self.assertTrue(hasattr(base.logger, 'warn'))
        self.assertTrue(hasattr(base.logger, 'error'))
        self.assertTrue(hasattr(base.logger, 'debug'))

        with self.assertNotRaises(Exception):
            foo.hello()
            foo.logger.warn('this is a warning')

        foo = Foo(logger = logging.getLogger('custom-logger'))

        self.assertTrue(hasattr(foo, 'logger'))
        self.assertIsInstance(base.logger, logging.Logger)
        self.assertTrue(hasattr(base.logger, 'log'))
        self.assertTrue(hasattr(base.logger, 'info'))
        self.assertTrue(hasattr(base.logger, 'warn'))
        self.assertTrue(hasattr(base.logger, 'error'))
        self.assertTrue(hasattr(base.logger, 'debug'))

        with self.assertNotRaises(Exception):
            foo.hello()
            foo.logger.warn('this is a warning')

    def test___repr__(self):
        base = mybase.Base()

        self.assertTrue(hasattr(base, '__repr__'))
        self.assertTrue(callable(base.__repr__))

        self.assertIsInstance(repr(base), str)
        self.assertEqual(repr(base), '<MyBase logger=True>')

        class Foo(mybase.Base):
            pass

        foo = Foo()

        self.assertTrue(hasattr(base, '__repr__'))
        self.assertTrue(callable(base.__repr__))

        self.assertIsInstance(repr(foo), str)
        self.assertEqual(repr(foo), '<Foo logger=True>')

    def test___str__(self):
        base = mybase.Base()

        self.assertTrue(hasattr(base, '__str__'))
        self.assertTrue(callable(base.__str__))

        self.assertIsInstance(str(base), str)
        self.assertEqual(str(base), '<MyBase logger=True>')

        class Foo(mybase.Base):
            pass

        foo = Foo()

        self.assertTrue(hasattr(foo, '__str__'))
        self.assertTrue(callable(foo.__str__))

        self.assertIsInstance(str(foo), str)
        self.assertEqual(str(foo), '<Foo logger=True>')

    def test___bool__(self):
        base = mybase.Base()

        self.assertTrue(hasattr(base, '__bool__'))
        self.assertTrue(callable(base.__bool__))

        self.assertTrue(base)

        class Foo(mybase.Base):
            pass

        foo = Foo()

        self.assertTrue(hasattr(foo, '__bool__'))
        self.assertTrue(callable(foo.__bool__))

        self.assertTrue(foo)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
