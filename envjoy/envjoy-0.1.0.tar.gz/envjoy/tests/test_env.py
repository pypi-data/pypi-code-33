
# =========================================
#       IMPORTS
# --------------------------------------

from __future__ import print_function # Python 2

import rootpath

rootpath.append()

from envjoy.tests import helper

import envjoy
import inspecta
import json

from os import environ
from collections import Iterable, Iterator, OrderedDict
from six import PY2, PY3, string_types

environ['COLORS'] = 'true' # lower prio
environ['VERBOSE'] = 'true' # lower prio

environ['ENV_COLORS'] = 'false' # higher prio
environ['ENV_VERBOSE'] = 'false' # higher prio


# =========================================
#       HELPERS
# --------------------------------------

def env_get(key, default = None):
    return environ.get(key, default)

def env_set(key, value):
    environ[key] = str(value)

def env_del(key):
    try:
        del environ[key]
    except:
        pass

def env_clear():
    for key in environ.keys():
        env_del(key)


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(envjoy)

    def test_get(self):
        self.assertTrue(hasattr(envjoy.env, 'get'))
        self.assertTrue(callable(envjoy.env.get))

        environ.clear()

        self.assertDeepEqual(envjoy.env.get('FOO'), None)
        self.assertDeepEqual(envjoy.env.get('BAR'), None)

        environ['FOO'] = '0'

        self.assertDeepEqual(envjoy.env.get('FOO'), 0)
        self.assertDeepEqual(envjoy.env.get('FOO', bool), False)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 0)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 0.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '0')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (0,))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [0])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '1'

        self.assertDeepEqual(envjoy.env.get('FOO'), 1)
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 1)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 1.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '1')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (1,))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [1])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '-1'

        self.assertDeepEqual(envjoy.env.get('FOO'), -1)
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), -1)
        self.assertDeepEqual(envjoy.env.get('FOO', float), -1.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '-1')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (-1,))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [-1])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '12.34'

        self.assertDeepEqual(envjoy.env.get('FOO'), 12.34)
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 12.34)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '12.34')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (12.34,))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [12.34])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '-12.34'

        self.assertDeepEqual(envjoy.env.get('FOO'), -12.34)
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), -12)
        self.assertDeepEqual(envjoy.env.get('FOO', float), -12.34)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '-12.34')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (-12.34,))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [-12.34])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = 'foo bar baz 1 2 3'

        self.assertDeepEqual(envjoy.env.get('FOO'), 'foo bar baz 1 2 3')
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), 'foo bar baz 1 2 3')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo bar baz 1 2 3',))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo bar baz 1 2 3'])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = 'foo,bar,baz,1,2,3'

        self.assertDeepEqual(envjoy.env.get('FOO'), 'foo,bar,baz,1,2,3')
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), 'foo,bar,baz,1,2,3')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo,bar,baz,1,2,3',))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo,bar,baz,1,2,3'])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = 'foo, bar, baz, 1, 2, 3'

        self.assertDeepEqual(envjoy.env.get('FOO'), 'foo, bar, baz, 1, 2, 3')
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), 'foo, bar, baz, 1, 2, 3')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo, bar, baz, 1, 2, 3',))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo, bar, baz, 1, 2, 3'])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '(foo,bar,baz,1,2,3)'

        # self.assertDeepEqual(envjoy.env.get('FOO'), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '(foo,bar,baz,1,2,3)')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '("foo","bar","baz",1,2,3)'

        self.assertDeepEqual(envjoy.env.get('FOO'), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '("foo","bar","baz",1,2,3)')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '((foo,bar),baz,(1,2,3))'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '((foo,bar),baz,(1,2,3))')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, 2, 3]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '(("foo","bar"),"baz",(1,2,3))'

        self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(("foo","bar"),"baz",(1,2,3))')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, 2, 3]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '([foo,bar],baz,[1,2,3])'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 'bar'], 'baz', [1, 2, 3]))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '([foo,bar],baz,[1,2,3])')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, 2, 3]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '(["foo","bar"],"baz",[1,2,3])'

        self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 'bar'], 'baz', [1, 2, 3]))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(["foo","bar"],"baz",[1,2,3])')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, 2, 3]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '(foo, bar, baz, 1, 2, 3)'

        # self.assertDeepEqual(envjoy.env.get('FOO'), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '(foo, bar, baz, 1, 2, 3)')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '("foo", "bar", "baz", 1, 2, 3)'

        self.assertDeepEqual(envjoy.env.get('FOO'), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '("foo", "bar", "baz", 1, 2, 3)')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '((foo, bar), baz, (1, (2, 3)))'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '((foo, bar), baz, (1, (2, 3)))')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '(("foo", "bar"), "baz", (1, (2, 3)))'

        self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(("foo", "bar"), "baz", (1, (2, 3)))')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '([foo, bar], baz, [1, [2, 3]])'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 'bar'], 'baz', [1, [2, 3]]))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '([foo, bar], baz, [1, [2, 3]])')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '(["foo", "bar"], "baz", [1, [2, 3]])'

        self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 'bar'], 'baz', [1, [2, 3]]))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(["foo", "bar"], "baz", [1, [2, 3]])')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[foo,bar,baz,1,2,3]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[foo,bar,baz,1,2,3]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '["foo","bar","baz",1,2,3]'

        self.assertDeepEqual(envjoy.env.get('FOO'), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '["foo","bar","baz",1,2,3]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[(foo,bar),baz,(1,(2,3))]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[(foo,bar),baz,(1,(2,3))]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '[("foo","bar"),"baz",(1,(2,3))]'

        self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 'bar'), 'baz', (1, (2, 3))])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '[("foo","bar"),"baz",(1,(2,3))]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[[foo,bar],baz,[1,[2,3]]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[[foo,bar],baz,[1,[2,3]]]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '[["foo","bar"],"baz",[1,[2,3]]]'

        self.assertDeepEqual(envjoy.env.get('FOO'), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '[["foo","bar"],"baz",[1,[2,3]]]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[foo, bar, baz, 1, 2, 3]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[foo, bar, baz, 1, 2, 3]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '["foo", "bar", "baz", 1, 2, 3]'

        self.assertDeepEqual(envjoy.env.get('FOO'), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '["foo", "bar", "baz", 1, 2, 3]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[(foo, bar), baz, (1, (2, 3))]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[(foo, bar), baz, (1, (2, 3))]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '[("foo", "bar"), "baz", (1, (2, 3))]'

        self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 'bar'), 'baz', (1, (2, 3))])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '[("foo", "bar"), "baz", (1, (2, 3))]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '[[foo, bar], baz, [1, [2, 3]]]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[[foo, bar], baz, [1, [2, 3]]]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = '[["foo", "bar"], "baz", [1, [2, 3]]]'

        self.assertDeepEqual(envjoy.env.get('FOO'), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '[["foo", "bar"], "baz", [1, [2, 3]]]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        # environ['FOO'] = '((foo, 1), (bar, 2))'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '((foo, 1), (bar, 2))')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        environ['FOO'] = '(("foo", 1), ("bar", 2))'

        self.assertDeepEqual(envjoy.env.get('FOO'), (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(("foo", 1), ("bar", 2))')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        # environ['FOO'] = '[(foo, 1), (bar, 2)]'

        # self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 1), ('bar', 2)])
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '[(foo, 1), (bar, 2)]')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        environ['FOO'] = '[("foo", 1), ("bar", 2)]'

        self.assertDeepEqual(envjoy.env.get('FOO'), [('foo', 1), ('bar', 2)])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '[("foo", 1), ("bar", 2)]')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        # environ['FOO'] = '([foo, 1], [bar, 2])'

        # self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 1], ['bar', 2]))
        # self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        # self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        # self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        # self.assertDeepEqual(envjoy.env.get('FOO', str), '([foo, 1], [bar, 2])')
        # self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        environ['FOO'] = '(["foo", 1], ["bar", 2])'

        self.assertDeepEqual(envjoy.env.get('FOO'), (['foo', 1], ['bar', 2]))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 12)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 12.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), '(["foo", 1], ["bar", 2])')
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2})

        environ['FOO'] = str(('foo', 'bar', 'baz', 1, 2, 3))

        self.assertDeepEqual(envjoy.env.get('FOO'), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), "('foo', 'bar', 'baz', 1, 2, 3)")
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = str(['foo', 'bar', 'baz', 1, 2, 3])

        self.assertDeepEqual(envjoy.env.get('FOO'), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)
        self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
        self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
        self.assertDeepEqual(envjoy.env.get('FOO', str), "['foo', 'bar', 'baz', 1, 2, 3]")
        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env.get('FOO', list), ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {})

        environ['FOO'] = str({'foo': 1, 'bar': 2, 'baz': 3})

        self.assertDeepEqual(envjoy.env.get('FOO'), {'foo': 1, 'bar': 2, 'baz': 3})
        self.assertDeepEqual(envjoy.env.get('FOO', bool), True)

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(envjoy.env['FOO', int], 213)
            self.assertDeepEqual(envjoy.env['FOO', float], 213.0)
            self.assertDeepEqual(envjoy.env['FOO', str], "{'baz': 3, 'foo': 1, 'bar': 2}")
        except:
            self.assertDeepEqual(envjoy.env.get('FOO', int), 123)
            self.assertDeepEqual(envjoy.env.get('FOO', float), 123.0)
            self.assertDeepEqual(envjoy.env.get('FOO', str), "{'foo': 1, 'bar': 2, 'baz': 3}")

        self.assertDeepEqual(envjoy.env.get('FOO', tuple), ({'bar': 2, 'baz': 3, 'foo': 1},))
        self.assertDeepEqual(envjoy.env.get('FOO', list), [{'bar': 2, 'baz': 3, 'foo': 1}])
        self.assertDeepEqual(envjoy.env.get('FOO', dict), {'foo': 1, 'bar': 2, 'baz': 3})

    def test_set(self):
        self.assertTrue(hasattr(envjoy.env, 'set'))
        self.assertTrue(callable(envjoy.env.set))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2')])

        envjoy.env.set('BAZ', 3)

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2'), ('BAZ', '3')])

        with self.assertRaises(Exception):
            envjoy.env.set('FOO')

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', None)

        self.assertDeepEqual(list(environ.items()), [('FOO', ''), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', True)

        self.assertDeepEqual(list(environ.items()), [('FOO', 'True'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', 'true')

        self.assertDeepEqual(list(environ.items()), [('FOO', 'true'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', 0)

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', '0')

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', 0.01)

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', '0.01')

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', 'foo bar baz 1 2 3')

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo bar baz 1 2 3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', 'foo,bar,baz,1,2,3')

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo,bar,baz,1,2,3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', '(foo,bar,baz,1,2,3)')

        self.assertDeepEqual(list(environ.items()), [('FOO', '(foo,bar,baz,1,2,3)'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', '[foo,bar,baz,1,2,3]')

        self.assertDeepEqual(list(environ.items()), [('FOO', '[foo,bar,baz,1,2,3]'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', ('foo', 'bar', 'baz', 1, 2, 3))

        self.assertDeepEqual(list(environ.items()), [('FOO', "('foo', 'bar', 'baz', 1, 2, 3)"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', ['foo', 'bar', 'baz', 1, 2, 3])

        self.assertDeepEqual(list(environ.items()), [('FOO', "['foo', 'bar', 'baz', 1, 2, 3]"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', {'foo': 1, 'bar': 2, 'baz': 3})

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'bar': 2, 'foo': 1, 'baz': 3}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', {'foo': {'bar': {'baz': True}}})

        self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': {'bar': {'baz': True}}}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.set('FOO', OrderedDict({'foo': 1, 'bar': 2, 'baz': 3}))

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'baz': 3, 'foo': 1, 'bar': 2}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

    def test_delete(self):
        self.assertTrue(hasattr(envjoy.env, 'delete'))
        self.assertTrue(callable(envjoy.env.delete))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        envjoy.env.delete('BAZ')

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        envjoy.env.delete('FOO')

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        envjoy.env.delete('BAR')

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        envjoy.env.delete('bar')

        self.assertDeepEqual(list(environ.keys()), [])

    def test_exists(self):
        self.assertTrue(hasattr(envjoy.env, 'exists'))
        self.assertTrue(callable(envjoy.env.exists))

        environ.clear()

        self.assertDeepEqual(envjoy.env.exists('XXX'), False)
        self.assertDeepEqual(envjoy.env.exists('BOOL'), False)
        self.assertDeepEqual(envjoy.env.exists('INT'), False)
        self.assertDeepEqual(envjoy.env.exists('FLOAT'), False)
        self.assertDeepEqual(envjoy.env.exists('TUPLE'), False)
        self.assertDeepEqual(envjoy.env.exists('LIST'), False)
        self.assertDeepEqual(envjoy.env.exists('DICT'), False)

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(envjoy.env.exists('XXX'), False)
        self.assertDeepEqual(envjoy.env.exists('BOOL'), True)
        self.assertDeepEqual(envjoy.env.exists('INT'), True)
        self.assertDeepEqual(envjoy.env.exists('FLOAT'), True)
        self.assertDeepEqual(envjoy.env.exists('TUPLE'), True)
        self.assertDeepEqual(envjoy.env.exists('LIST'), True)
        self.assertDeepEqual(envjoy.env.exists('DICT'), True)

    def test_clear(self):
        self.assertTrue(hasattr(envjoy.env, 'clear'))
        self.assertTrue(callable(envjoy.env.clear))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        envjoy.env.clear()

        self.assertDeepEqual(list(environ.keys()), [])

    def test_size(self):
        self.assertTrue(hasattr(envjoy.env, 'size'))
        self.assertTrue(callable(envjoy.env.size))

        self.assertIsInstance(envjoy.env.size(), int)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(envjoy.env.size(), 6)

    def test_inspect(self):
        self.assertTrue(hasattr(envjoy.env, 'inspect'))
        self.assertTrue(callable(envjoy.env.inspect))

        environ.clear()

        environ['FOO'] = '1'

        self.assertIsInstance(envjoy.env.inspect(), string_types)

        self.assertDeepEqual(envjoy.env.inspect(), inspecta.inspect({'FOO': 1}))

    def test_print(self):
        self.assertTrue(hasattr(envjoy.env, 'print'))
        self.assertTrue(callable(envjoy.env.print))

        with self.assertNotRaises(Exception):
            envjoy.env.print()

    def test_keys(self):
        self.assertTrue(hasattr(envjoy.env, 'keys'))
        self.assertTrue(callable(envjoy.env.keys))

        self.assertIsInstance(envjoy.env.keys(), Iterable)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(list(envjoy.env.keys()), [
            'BOOL',
            'INT',
            'FLOAT',
            'TUPLE',
            'LIST',
            'DICT',
        ])

    def test_values(self):
        self.assertTrue(hasattr(envjoy.env, 'values'))
        self.assertTrue(callable(envjoy.env.values))

        self.assertIsInstance(envjoy.env.values(), Iterable)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(list(envjoy.env.values()), [
            True,
            1,
            1.01,
            (1, 2, 3),
            [1, 2, 3],
            {'foo': [1, 2, 3]},
        ])

    def test_items(self):
        self.assertTrue(hasattr(envjoy.env, 'items'))
        self.assertTrue(callable(envjoy.env.items))

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(list(envjoy.env.items()), [
            ('BOOL', True),
            ('INT', 1),
            ('FLOAT', 1.01),
            ('TUPLE', (1, 2, 3)),
            ('LIST', [1, 2, 3]),
            ('DICT', {'foo': [1, 2, 3]}),
        ])

    def test_tolist(self):
        self.assertTrue(hasattr(envjoy.env, 'tolist'))
        self.assertTrue(callable(envjoy.env.tolist))

        self.assertIsInstance(envjoy.env.tolist(), list)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(envjoy.env.tolist(), [
            ('BOOL', True),
            ('INT', 1),
            ('FLOAT', 1.01),
            ('TUPLE', (1, 2, 3)),
            ('LIST', [1, 2, 3]),
            ('DICT', {'foo': [1, 2, 3]}),
        ])

    def test_todict(self):
        self.assertTrue(hasattr(envjoy.env, 'todict'))
        self.assertTrue(callable(envjoy.env.todict))

        self.assertIsInstance(envjoy.env.todict(), dict)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(envjoy.env.todict(), {
            'BOOL': True,
            'INT': 1,
            'FLOAT': 1.01,
            'TUPLE': (1, 2, 3),
            'LIST': [1, 2, 3],
            'DICT': {'foo': [1, 2, 3]},
        })

    def test___getitem__(self):
        self.assertTrue(hasattr(envjoy.env, '__getitem__'))
        self.assertTrue(callable(envjoy.env.__getitem__))

        environ.clear()

        self.assertDeepEqual(envjoy.env['FOO'], None)
        self.assertDeepEqual(envjoy.env['BAR'], None)

        environ['FOO'] = '0'

        self.assertDeepEqual(envjoy.env['FOO'], 0)
        self.assertDeepEqual(envjoy.env['FOO', bool], False)
        self.assertDeepEqual(envjoy.env['FOO', int], 0)
        self.assertDeepEqual(envjoy.env['FOO', float], 0.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '0')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (0,))
        self.assertDeepEqual(envjoy.env['FOO', list], [0])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '1'

        self.assertDeepEqual(envjoy.env['FOO'], 1)
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 1)
        self.assertDeepEqual(envjoy.env['FOO', float], 1.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '1')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (1,))
        self.assertDeepEqual(envjoy.env['FOO', list], [1])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '-1'

        self.assertDeepEqual(envjoy.env['FOO'], -1)
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], -1)
        self.assertDeepEqual(envjoy.env['FOO', float], -1.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '-1')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (-1,))
        self.assertDeepEqual(envjoy.env['FOO', list], [-1])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '12.34'

        self.assertDeepEqual(envjoy.env['FOO'], 12.34)
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 12)
        self.assertDeepEqual(envjoy.env['FOO', float], 12.34)
        self.assertDeepEqual(envjoy.env['FOO', str], '12.34')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (12.34,))
        self.assertDeepEqual(envjoy.env['FOO', list], [12.34])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '-12.34'

        self.assertDeepEqual(envjoy.env['FOO'], -12.34)
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], -12)
        self.assertDeepEqual(envjoy.env['FOO', float], -12.34)
        self.assertDeepEqual(envjoy.env['FOO', str], '-12.34')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (-12.34,))
        self.assertDeepEqual(envjoy.env['FOO', list], [-12.34])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = 'foo bar baz 1 2 3'

        self.assertDeepEqual(envjoy.env['FOO'], 'foo bar baz 1 2 3')
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], 'foo bar baz 1 2 3')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo bar baz 1 2 3',))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo bar baz 1 2 3'])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = 'foo,bar,baz,1,2,3'

        self.assertDeepEqual(envjoy.env['FOO'], 'foo,bar,baz,1,2,3')
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], 'foo,bar,baz,1,2,3')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo,bar,baz,1,2,3',))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo,bar,baz,1,2,3'])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = 'foo, bar, baz, 1, 2, 3'

        self.assertDeepEqual(envjoy.env['FOO'], 'foo, bar, baz, 1, 2, 3')
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], 'foo, bar, baz, 1, 2, 3')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo, bar, baz, 1, 2, 3',))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo, bar, baz, 1, 2, 3'])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '(foo,bar,baz,1,2,3)'

        # self.assertDeepEqual(envjoy.env['FOO'], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '(foo,bar,baz,1,2,3)')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '("foo","bar","baz",1,2,3)'

        self.assertDeepEqual(envjoy.env['FOO'], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '("foo","bar","baz",1,2,3)')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '((foo,bar),baz,(1,2,3))'

        # self.assertDeepEqual(envjoy.env['FOO'], (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '((foo,bar),baz,(1,2,3))')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, 2, 3]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '(("foo","bar"),"baz",(1,2,3))'

        self.assertDeepEqual(envjoy.env['FOO'], (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(("foo","bar"),"baz",(1,2,3))')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, 2, 3]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '([foo,bar],baz,[1,2,3])'

        # self.assertDeepEqual(envjoy.env['FOO'], (['foo', 'bar'], 'baz', [1, 2, 3]))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '([foo,bar],baz,[1,2,3])')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, 2, 3)))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, 2, 3]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '(["foo","bar"],"baz",[1,2,3])'

        self.assertDeepEqual(envjoy.env['FOO'], (['foo', 'bar'], 'baz', [1, 2, 3]))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(["foo","bar"],"baz",[1,2,3])')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, 2, 3)))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, 2, 3]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '(foo, bar, baz, 1, 2, 3)'

        # self.assertDeepEqual(envjoy.env['FOO'], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '(foo, bar, baz, 1, 2, 3)')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '("foo", "bar", "baz", 1, 2, 3)'

        self.assertDeepEqual(envjoy.env['FOO'], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '("foo", "bar", "baz", 1, 2, 3)')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '((foo, bar), baz, (1, (2, 3)))'

        # self.assertDeepEqual(envjoy.env['FOO'], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '((foo, bar), baz, (1, (2, 3)))')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '(("foo", "bar"), "baz", (1, (2, 3)))'

        self.assertDeepEqual(envjoy.env['FOO'], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(("foo", "bar"), "baz", (1, (2, 3)))')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '([foo, bar], baz, [1, [2, 3]])'

        # self.assertDeepEqual(envjoy.env['FOO'], (['foo', 'bar'], 'baz', [1, [2, 3]]))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '([foo, bar], baz, [1, [2, 3]])')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '(["foo", "bar"], "baz", [1, [2, 3]])'

        self.assertDeepEqual(envjoy.env['FOO'], (['foo', 'bar'], 'baz', [1, [2, 3]]))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(["foo", "bar"], "baz", [1, [2, 3]])')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[foo,bar,baz,1,2,3]'

        # self.assertDeepEqual(envjoy.env['FOO'], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[foo,bar,baz,1,2,3]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '["foo","bar","baz",1,2,3]'

        self.assertDeepEqual(envjoy.env['FOO'], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '["foo","bar","baz",1,2,3]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[(foo,bar),baz,(1,(2,3))]'

        # self.assertDeepEqual(envjoy.env['FOO'], [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[(foo,bar),baz,(1,(2,3))]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '[("foo","bar"),"baz",(1,(2,3))]'

        self.assertDeepEqual(envjoy.env['FOO'], [('foo', 'bar'), 'baz', (1, (2, 3))])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '[("foo","bar"),"baz",(1,(2,3))]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[[foo,bar],baz,[1,[2,3]]'

        # self.assertDeepEqual(envjoy.env['FOO'], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[[foo,bar],baz,[1,[2,3]]]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '[["foo","bar"],"baz",[1,[2,3]]]'

        self.assertDeepEqual(envjoy.env['FOO'], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '[["foo","bar"],"baz",[1,[2,3]]]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[foo, bar, baz, 1, 2, 3]'

        # self.assertDeepEqual(envjoy.env['FOO'], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[foo, bar, baz, 1, 2, 3]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        # self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '["foo", "bar", "baz", 1, 2, 3]'

        self.assertDeepEqual(envjoy.env['FOO'], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '["foo", "bar", "baz", 1, 2, 3]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[(foo, bar), baz, (1, (2, 3))]'

        # self.assertDeepEqual(envjoy.env['FOO'], [('foo', 'bar'), 'baz', (1, (2, 3))])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[(foo, bar), baz, (1, (2, 3))]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '[("foo", "bar"), "baz", (1, (2, 3))]'

        self.assertDeepEqual(envjoy.env['FOO'], [('foo', 'bar'), 'baz', (1, (2, 3))])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '[("foo", "bar"), "baz", (1, (2, 3))]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '[[foo, bar], baz, [1, [2, 3]]]'

        # self.assertDeepEqual(envjoy.env['FOO'], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 123)
        # self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[[foo, bar], baz, [1, [2, 3]]]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = '[["foo", "bar"], "baz", [1, [2, 3]]]'

        self.assertDeepEqual(envjoy.env['FOO'], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '[["foo", "bar"], "baz", [1, [2, 3]]]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 'bar'), 'baz', (1, (2, 3))))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 'bar'], 'baz', [1, [2, 3]]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        # environ['FOO'] = '((foo, 1), (bar, 2))'

        # self.assertDeepEqual(envjoy.env['FOO'], (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 12)
        # self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '((foo, 1), (bar, 2))')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        environ['FOO'] = '(("foo", 1), ("bar", 2))'

        self.assertDeepEqual(envjoy.env['FOO'], (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 12)
        self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(("foo", 1), ("bar", 2))')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        # environ['FOO'] = '[(foo, 1), (bar, 2)]'

        # self.assertDeepEqual(envjoy.env['FOO'], [('foo', 1), ('bar', 2)])
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 12)
        # self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '[(foo, 1), (bar, 2)]')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        environ['FOO'] = '[("foo", 1), ("bar", 2)]'

        self.assertDeepEqual(envjoy.env['FOO'], [('foo', 1), ('bar', 2)])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 12)
        self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '[("foo", 1), ("bar", 2)]')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        # environ['FOO'] = '([foo, 1], [bar, 2])'

        # self.assertDeepEqual(envjoy.env['FOO'], (['foo', 1], ['bar', 2]))
        # self.assertDeepEqual(envjoy.env['FOO', bool], True)
        # self.assertDeepEqual(envjoy.env['FOO', int], 12)
        # self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        # self.assertDeepEqual(envjoy.env['FOO', str], '([foo, 1], [bar, 2])')
        # self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        # self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        # self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        environ['FOO'] = '(["foo", 1], ["bar", 2])'

        self.assertDeepEqual(envjoy.env['FOO'], (['foo', 1], ['bar', 2]))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 12)
        self.assertDeepEqual(envjoy.env['FOO', float], 12.0)
        self.assertDeepEqual(envjoy.env['FOO', str], '(["foo", 1], ["bar", 2])')
        self.assertDeepEqual(envjoy.env['FOO', tuple], (('foo', 1), ('bar', 2)))
        self.assertDeepEqual(envjoy.env['FOO', list], [['foo', 1], ['bar', 2]])
        self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2})

        environ['FOO'] = str(('foo', 'bar', 'baz', 1, 2, 3))

        self.assertDeepEqual(envjoy.env['FOO'], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], "('foo', 'bar', 'baz', 1, 2, 3)")
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = str(['foo', 'bar', 'baz', 1, 2, 3])

        self.assertDeepEqual(envjoy.env['FOO'], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', bool], True)
        self.assertDeepEqual(envjoy.env['FOO', int], 123)
        self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
        self.assertDeepEqual(envjoy.env['FOO', str], "['foo', 'bar', 'baz', 1, 2, 3]")
        self.assertDeepEqual(envjoy.env['FOO', tuple], ('foo', 'bar', 'baz', 1, 2, 3))
        self.assertDeepEqual(envjoy.env['FOO', list], ['foo', 'bar', 'baz', 1, 2, 3])
        self.assertDeepEqual(envjoy.env['FOO', dict], {})

        environ['FOO'] = str({'foo': 1, 'bar': 2, 'baz': 3})

        self.assertDeepEqual(envjoy.env['FOO'], {'foo': 1, 'bar': 2, 'baz': 3})
        self.assertDeepEqual(envjoy.env['FOO', bool], True)

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(envjoy.env['FOO', int], 213)
            self.assertDeepEqual(envjoy.env['FOO', float], 213.0)
            self.assertDeepEqual(envjoy.env['FOO', str], "{'baz': 3, 'foo': 1, 'bar': 2}")
        except:
            self.assertDeepEqual(envjoy.env['FOO', int], 123)
            self.assertDeepEqual(envjoy.env['FOO', float], 123.0)
            self.assertDeepEqual(envjoy.env['FOO', str], "{'foo': 1, 'bar': 2, 'baz': 3}")

        self.assertDeepEqual(envjoy.env['FOO', tuple], ({'bar': 2, 'baz': 3, 'foo': 1},))
        self.assertDeepEqual(envjoy.env['FOO', list], [{'bar': 2, 'baz': 3, 'foo': 1}])
        self.assertDeepEqual(envjoy.env['FOO', dict], {'foo': 1, 'bar': 2, 'baz': 3})

    def test___getattr__(self):
        self.assertTrue(hasattr(envjoy.env, '__getattr__'))
        self.assertTrue(callable(envjoy.env.__getattr__))

        environ.clear()

        self.assertDeepEqual(envjoy.env.FOO, None)
        self.assertDeepEqual(envjoy.env.BAR, None)

        environ['FOO'] = '0'

        self.assertDeepEqual(envjoy.env.FOO, 0)

        environ['FOO'] = '1'

        self.assertDeepEqual(envjoy.env.FOO, 1)

        environ['FOO'] = '-1'

        self.assertDeepEqual(envjoy.env.FOO, -1)

        environ['FOO'] = '12.34'

        self.assertDeepEqual(envjoy.env.FOO, 12.34)

        environ['FOO'] = '-12.34'

        self.assertDeepEqual(envjoy.env.FOO, -12.34)

        environ['FOO'] = 'foo bar baz 1 2 3'

        self.assertDeepEqual(envjoy.env.FOO, 'foo bar baz 1 2 3')

        environ['FOO'] = 'foo,bar,baz,1,2,3'

        self.assertDeepEqual(envjoy.env.FOO, 'foo,bar,baz,1,2,3')

        environ['FOO'] = 'foo, bar, baz, 1, 2, 3'

        self.assertDeepEqual(envjoy.env.FOO, 'foo, bar, baz, 1, 2, 3')

        # environ['FOO'] = '(foo,bar,baz,1,2,3)'

        # self.assertDeepEqual(envjoy.env.FOO, ('foo', 'bar', 'baz', 1, 2, 3))

        environ['FOO'] = '("foo","bar","baz",1,2,3)'

        self.assertDeepEqual(envjoy.env.FOO, ('foo', 'bar', 'baz', 1, 2, 3))

        # environ['FOO'] = '((foo,bar),baz,(1,2,3))'

        # self.assertDeepEqual(envjoy.env.FOO, (('foo', 'bar'), 'baz', (1, 2, 3)))

        environ['FOO'] = '(("foo","bar"),"baz",(1,2,3))'

        self.assertDeepEqual(envjoy.env.FOO, (('foo', 'bar'), 'baz', (1, 2, 3)))

        # environ['FOO'] = '([foo,bar],baz,[1,2,3])'

        # self.assertDeepEqual(envjoy.env.FOO, (['foo', 'bar'], 'baz', [1, 2, 3]))

        environ['FOO'] = '(["foo","bar"],"baz",[1,2,3])'

        self.assertDeepEqual(envjoy.env.FOO, (['foo', 'bar'], 'baz', [1, 2, 3]))

        # environ['FOO'] = '(foo, bar, baz, 1, 2, 3)'

        # self.assertDeepEqual(envjoy.env.FOO, ('foo', 'bar', 'baz', 1, 2, 3))

        environ['FOO'] = '("foo", "bar", "baz", 1, 2, 3)'

        self.assertDeepEqual(envjoy.env.FOO, ('foo', 'bar', 'baz', 1, 2, 3))

        # environ['FOO'] = '((foo, bar), baz, (1, (2, 3)))'

        # self.assertDeepEqual(envjoy.env.FOO, (('foo', 'bar'), 'baz', (1, (2, 3))))

        environ['FOO'] = '(("foo", "bar"), "baz", (1, (2, 3)))'

        self.assertDeepEqual(envjoy.env.FOO, (('foo', 'bar'), 'baz', (1, (2, 3))))

        # environ['FOO'] = '([foo, bar], baz, [1, [2, 3]])'

        # self.assertDeepEqual(envjoy.env.FOO, (['foo', 'bar'], 'baz', [1, [2, 3]]))

        environ['FOO'] = '(["foo", "bar"], "baz", [1, [2, 3]])'

        self.assertDeepEqual(envjoy.env.FOO, (['foo', 'bar'], 'baz', [1, [2, 3]]))

        # environ['FOO'] = '[foo,bar,baz,1,2,3]'

        # self.assertDeepEqual(envjoy.env.FOO, ['foo', 'bar', 'baz', 1, 2, 3])

        environ['FOO'] = '["foo","bar","baz",1,2,3]'

        self.assertDeepEqual(envjoy.env.FOO, ['foo', 'bar', 'baz', 1, 2, 3])

        # environ['FOO'] = '[(foo,bar),baz,(1,(2,3))]'

        # self.assertDeepEqual(envjoy.env.FOO, [('foo', 'bar'), 'baz', (1, (2, 3))])

        environ['FOO'] = '[("foo","bar"),"baz",(1,(2,3))]'

        self.assertDeepEqual(envjoy.env.FOO, [('foo', 'bar'), 'baz', (1, (2, 3))])

        # environ['FOO'] = '[[foo,bar],baz,[1,[2,3]]'

        # self.assertDeepEqual(envjoy.env.FOO, [['foo', 'bar'], 'baz', [1, [2, 3]]])

        environ['FOO'] = '[["foo","bar"],"baz",[1,[2,3]]]'

        self.assertDeepEqual(envjoy.env.FOO, [['foo', 'bar'], 'baz', [1, [2, 3]]])

        # environ['FOO'] = '[foo, bar, baz, 1, 2, 3]'

        # self.assertDeepEqual(envjoy.env.FOO, ['foo', 'bar', 'baz', 1, 2, 3])

        environ['FOO'] = '["foo", "bar", "baz", 1, 2, 3]'

        self.assertDeepEqual(envjoy.env.FOO, ['foo', 'bar', 'baz', 1, 2, 3])

        # environ['FOO'] = '[(foo, bar), baz, (1, (2, 3))]'

        # self.assertDeepEqual(envjoy.env.FOO, [('foo', 'bar'), 'baz', (1, (2, 3))])

        environ['FOO'] = '[("foo", "bar"), "baz", (1, (2, 3))]'

        self.assertDeepEqual(envjoy.env.FOO, [('foo', 'bar'), 'baz', (1, (2, 3))])

        # environ['FOO'] = '[[foo, bar], baz, [1, [2, 3]]]'

        # self.assertDeepEqual(envjoy.env.FOO, [['foo', 'bar'], 'baz', [1, [2, 3]]])

        environ['FOO'] = '[["foo", "bar"], "baz", [1, [2, 3]]]'

        self.assertDeepEqual(envjoy.env.FOO, [['foo', 'bar'], 'baz', [1, [2, 3]]])

        # environ['FOO'] = '((foo, 1), (bar, 2))'

        # self.assertDeepEqual(envjoy.env.FOO, (('foo', 1), ('bar', 2)))

        environ['FOO'] = '(("foo", 1), ("bar", 2))'

        self.assertDeepEqual(envjoy.env.FOO, (('foo', 1), ('bar', 2)))

        # environ['FOO'] = '[(foo, 1), (bar, 2)]'

        # self.assertDeepEqual(envjoy.env.FOO, [('foo', 1), ('bar', 2)])

        environ['FOO'] = '[("foo", 1), ("bar", 2)]'

        self.assertDeepEqual(envjoy.env.FOO, [('foo', 1), ('bar', 2)])

        # environ['FOO'] = '([foo, 1], [bar, 2])'

        # self.assertDeepEqual(envjoy.env.FOO, (['foo', 1], ['bar', 2]))

        environ['FOO'] = '(["foo", 1], ["bar", 2])'

        self.assertDeepEqual(envjoy.env.FOO, (['foo', 1], ['bar', 2]))

        environ['FOO'] = str(('foo', 'bar', 'baz', 1, 2, 3))

        self.assertDeepEqual(envjoy.env.FOO, ('foo', 'bar', 'baz', 1, 2, 3))

        environ['FOO'] = str(['foo', 'bar', 'baz', 1, 2, 3])

        self.assertDeepEqual(envjoy.env.FOO, ['foo', 'bar', 'baz', 1, 2, 3])

        environ['FOO'] = str({'foo': 1, 'bar': 2, 'baz': 3})

        self.assertDeepEqual(envjoy.env.FOO, {'foo': 1, 'bar': 2, 'baz': 3})

    def test___setitem__(self):
        self.assertTrue(hasattr(envjoy.env, '__setitem__'))
        self.assertTrue(callable(envjoy.env.__setitem__))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2')])

        envjoy.env['BAZ'] = 3

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = None

        self.assertDeepEqual(list(environ.items()), [('FOO', ''), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = True

        self.assertDeepEqual(list(environ.items()), [('FOO', 'True'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = 'true'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'true'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = 0

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = '0'

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = 0.01

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = '0.01'

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = 'foo bar baz 1 2 3'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo bar baz 1 2 3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = 'foo,bar,baz,1,2,3'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo,bar,baz,1,2,3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = '(foo,bar,baz,1,2,3)'

        self.assertDeepEqual(list(environ.items()), [('FOO', '(foo,bar,baz,1,2,3)'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = '[foo,bar,baz,1,2,3]'

        self.assertDeepEqual(list(environ.items()), [('FOO', '[foo,bar,baz,1,2,3]'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = ('foo', 'bar', 'baz', 1, 2, 3)

        self.assertDeepEqual(list(environ.items()), [('FOO', "('foo', 'bar', 'baz', 1, 2, 3)"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = ['foo', 'bar', 'baz', 1, 2, 3]

        self.assertDeepEqual(list(environ.items()), [('FOO', "['foo', 'bar', 'baz', 1, 2, 3]"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = {'foo': 1, 'bar': 2, 'baz': 3}

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'bar': 2, 'foo': 1, 'baz': 3}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = {'foo': {'bar': {'baz': True}}}

        self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': {'bar': {'baz': True}}}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env['FOO'] = OrderedDict({'foo': 1, 'bar': 2, 'baz': 3})

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'baz': 3, 'foo': 1, 'bar': 2}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

    def test___setattr__(self):
        self.assertTrue(hasattr(envjoy.env, '__setattr__'))
        self.assertTrue(callable(envjoy.env.__setattr__))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2')])

        envjoy.env.BAZ = 3

        self.assertDeepEqual(list(environ.items()), [('FOO', '1'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = None

        self.assertDeepEqual(list(environ.items()), [('FOO', ''), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = True

        self.assertDeepEqual(list(environ.items()), [('FOO', 'True'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = 'true'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'true'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = 0

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = '0'

        self.assertDeepEqual(list(environ.items()), [('FOO', '0'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = 0.01

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = '0.01'

        self.assertDeepEqual(list(environ.items()), [('FOO', '0.01'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = 'foo bar baz 1 2 3'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo bar baz 1 2 3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = 'foo,bar,baz,1,2,3'

        self.assertDeepEqual(list(environ.items()), [('FOO', 'foo,bar,baz,1,2,3'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = '(foo,bar,baz,1,2,3)'

        self.assertDeepEqual(list(environ.items()), [('FOO', '(foo,bar,baz,1,2,3)'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = '[foo,bar,baz,1,2,3]'

        self.assertDeepEqual(list(environ.items()), [('FOO', '[foo,bar,baz,1,2,3]'), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = ('foo', 'bar', 'baz', 1, 2, 3)

        self.assertDeepEqual(list(environ.items()), [('FOO', "('foo', 'bar', 'baz', 1, 2, 3)"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = ['foo', 'bar', 'baz', 1, 2, 3]

        self.assertDeepEqual(list(environ.items()), [('FOO', "['foo', 'bar', 'baz', 1, 2, 3]"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = {'foo': 1, 'bar': 2, 'baz': 3}

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'bar': 2, 'foo': 1, 'baz': 3}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = {'foo': {'bar': {'baz': True}}}

        self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': {'bar': {'baz': True}}}"), ('bar', '2'), ('BAZ', '3')])

        envjoy.env.FOO = OrderedDict({'foo': 1, 'bar': 2, 'baz': 3})

        # NOTE: no consistency within Python's major versions even >:'(
        try:
            self.assertDeepEqual(list(environ.items()), [('BAZ', '3'), ('FOO', "{'baz': 3, 'foo': 1, 'bar': 2}"), ('bar', '2')])
        except:
            self.assertDeepEqual(list(environ.items()), [('FOO', "{'foo': 1, 'bar': 2, 'baz': 3}"), ('bar', '2'), ('BAZ', '3')])

    def test___delitem__(self):
        self.assertTrue(hasattr(envjoy.env, '__delitem__'))
        self.assertTrue(callable(envjoy.env.__delitem__))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        del envjoy.env['BAZ']

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        del envjoy.env['FOO']

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        del envjoy.env['BAR']

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        del envjoy.env['bar']

        self.assertDeepEqual(list(environ.keys()), [])

    def test___delattr__(self):
        self.assertTrue(hasattr(envjoy.env, '__delattr__'))
        self.assertTrue(callable(envjoy.env.__delattr__))

        environ.clear()

        environ['FOO'] = '1'
        environ['bar'] = '2'

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        del envjoy.env.BAZ

        self.assertDeepEqual(list(environ.keys()), ['FOO', 'bar'])

        del envjoy.env.FOO

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        del envjoy.env.BAR

        self.assertDeepEqual(list(environ.keys()), ['bar'])

        del envjoy.env.bar

        self.assertDeepEqual(list(environ.keys()), [])

    def test___contains__(self):
        self.assertTrue(hasattr(envjoy.env, '__contains__'))
        self.assertTrue(callable(envjoy.env.__contains__))

        environ.clear()

        self.assertDeepEqual(('XXX' in envjoy.env), False)
        self.assertDeepEqual(('BOOL' in envjoy.env), False)
        self.assertDeepEqual(('INT' in envjoy.env), False)
        self.assertDeepEqual(('FLOAT' in envjoy.env), False)
        self.assertDeepEqual(('TUPLE' in envjoy.env), False)
        self.assertDeepEqual(('LIST' in envjoy.env), False)
        self.assertDeepEqual(('DICT' in envjoy.env), False)

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(('XXX' in envjoy.env), False)
        self.assertDeepEqual(('BOOL' in envjoy.env), True)
        self.assertDeepEqual(('INT' in envjoy.env), True)
        self.assertDeepEqual(('FLOAT' in envjoy.env), True)
        self.assertDeepEqual(('TUPLE' in envjoy.env), True)
        self.assertDeepEqual(('LIST' in envjoy.env), True)
        self.assertDeepEqual(('DICT' in envjoy.env), True)

    def test___len__(self):
        self.assertTrue(hasattr(envjoy.env, '__len__'))
        self.assertTrue(callable(envjoy.env.__len__))

        self.assertIsInstance(len(envjoy.env), int)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(len(envjoy.env), 6)

    def test___iter__(self):
        self.assertTrue(hasattr(envjoy.env, '__iter__'))
        self.assertTrue(callable(envjoy.env.__iter__))

        self.assertIsInstance(iter(envjoy.env), Iterable)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        self.assertDeepEqual(list(iter(envjoy.env)), [
            ('BOOL', True),
            ('INT', 1),
            ('FLOAT', 1.01),
            ('TUPLE', (1, 2, 3)),
            ('LIST', [1, 2, 3]),
            ('DICT', {'foo': [1, 2, 3]}),
        ])

    def test___repr__(self):
        self.assertTrue(hasattr(envjoy.env, '__repr__'))
        self.assertTrue(callable(envjoy.env.__repr__))

        self.assertIsInstance(repr(envjoy.env), str)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        # NOTE: Python 2 vs Python 3
        self.assertDeepEqual(eval(repr(envjoy.env)), eval("{'BOOL': True, 'INT': 1, 'FLOAT': 1.01, 'TUPLE': (1, 2, 3), 'LIST': [1, 2, "
 "3], 'DICT': {'foo': [1, 2, 3]}}"))


    def test___str__(self):
        self.assertTrue(hasattr(envjoy.env, '__str__'))
        self.assertTrue(callable(envjoy.env.__str__))

        self.assertIsInstance(str(envjoy.env), str)

        environ.clear()

        environ['BOOL'] = str(True)
        environ['INT'] = str(1)
        environ['FLOAT'] = str(1.01)
        environ['TUPLE'] = str((1, 2, 3))
        environ['LIST'] = str([1, 2, 3])
        environ['DICT'] = str({'foo': [1, 2, 3]})

        # NOTE: Python 2 vs Python 3
        self.assertDeepEqual(eval(str(envjoy.env)), eval("{'BOOL': True, 'INT': 1, 'FLOAT': 1.01, 'TUPLE': (1, 2, 3), 'LIST': [1, 2, "
 "3], 'DICT': {'foo': [1, 2, 3]}}"))

    def test___bool__(self):
        self.assertTrue(hasattr(envjoy.env, '__bool__'))
        self.assertTrue(callable(envjoy.env.__bool__))

        self.assertTrue(envjoy.env)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
