
# =========================================
#       IMPORTS
# --------------------------------------

import rootpath

rootpath.append()

from connection_uri.tests import helper

import connection_uri as uri

from six import PY2, PY3, string_types


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(uri)

    def test_serialize(self):
        for serializer_method in ['serialize', 'pack', 'stringify']:
            self.assertTrue(hasattr(uri, serializer_method))

            serialize = getattr(uri, serializer_method)

            self.assertTrue(callable(serialize))

            with self.assertNotRaises(uri.Error):
                result = serialize(None)
                self.assertEqual(result, None)

                # single host

                result = serialize({'path': '/'})
                self.assertEqual(result, 'http://localhost:80/')

                result = serialize({'host': 'localhost'})
                self.assertEqual(result, 'http://localhost:80/')

                result = serialize({'host': 'localhost', 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000/')

                result = serialize({'protocol': 'http', 'host': 'localhost', 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000/')

                result = serialize({'protocol': 'https', 'host': 'localhost', 'port': 3000})
                self.assertEqual(result, 'https://localhost:3000/')

                result = serialize({'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:80/namespace')

                result = serialize({'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:80/namespace/')

                result = serialize({'host': 'localhost', 'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:80/namespace')

                result = serialize({'host': 'localhost', 'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:80/namespace/')

                result = serialize({'path': '/localhost/namespace'})
                self.assertEqual(result, 'http://localhost:80/localhost/namespace')

                result = serialize({'path': '/localhost/namespace/'})
                self.assertEqual(result, 'http://localhost:80/localhost/namespace/')

                result = serialize({'host': 'localhost', 'port': 3000, 'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:3000/namespace')

                result = serialize({'host': 'localhost', 'port': 3000, 'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:3000/namespace/')

                result = serialize({'protocol': 'http', 'host': 'localhost', 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000/')

                result = serialize({'protocol': 'https', 'host': 'localhost', 'port': 3000})
                self.assertEqual(result, 'https://localhost:3000/')

                result = serialize({'protocol': 'foo', 'host': 'ds143144-a0.mlab.com', 'port': 43144, 'auth': 'm+4.gTe~5e^(:m+4.gTe~5e^(', 'path': '/bar-baz'})
                self.assertEqual(result, 'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144/bar-baz')

                # multiple `host` (array<string>)

                result = serialize({'hosts': ['localhost', 'foohost']})
                self.assertEqual(result, 'http://localhost:80,foohost:80/')

                result = serialize({'hosts': ['localhost', 'foohost'], 'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:80,foohost:80/namespace')

                result = serialize({'hosts': ['localhost', 'foohost'], 'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:80,foohost:80/namespace/')

                # multiple `host` (array<string>) + single `port` (int)

                result = serialize({'hosts': ['localhost', 'foohost'], 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000,foohost:3000/')

                result = serialize({'protocol': 'http', 'hosts': ['localhost', 'foohost'], 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000,foohost:3000/')

                result = serialize({'protocol': 'https', 'hosts': ['localhost', 'foohost'], 'port': 3000})
                self.assertEqual(result, 'https://localhost:3000,foohost:3000/')

                result = serialize({'hosts': ['localhost', 'foohost'], 'port': 3000, 'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:3000,foohost:3000/namespace')

                result = serialize({'hosts': ['localhost', 'foohost'], 'port': 3000, 'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:3000,foohost:3000/namespace/')

                result = serialize({'protocol': 'http', 'hosts': ['localhost', 'foohost'], 'port': 3000})
                self.assertEqual(result, 'http://localhost:3000,foohost:3000/')

                result = serialize({'protocol': 'https', 'hosts': ['localhost', 'foohost'], 'port': 3000})
                self.assertEqual(result, 'https://localhost:3000,foohost:3000/')

                result = serialize({'protocol': 'foo', 'hosts': ['ds143144-a0.mlab.com', 'ds143144-a1.mlab.com'], 'port': 43144, 'auth': 'm+4.gTe~5e^(:m+4.gTe~5e^(', 'path': '/bar-baz'})
                self.assertEqual(result, 'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144,ds143144-a1.mlab.com:43144/bar-baz')

                # multiple `host` (array<string>) + multiple `port` (array<int>)

                result = serialize({'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001]})
                self.assertEqual(result, 'http://localhost:3000,foohost:3001/')

                result = serialize({'protocol': 'http', 'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001]})
                self.assertEqual(result, 'http://localhost:3000,foohost:3001/')

                result = serialize({'protocol': 'https', 'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001]})
                self.assertEqual(result, 'https://localhost:3000,foohost:3001/')

                result = serialize({'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001], 'path': '/namespace'})
                self.assertEqual(result, 'http://localhost:3000,foohost:3001/namespace')

                result = serialize({'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001], 'path': '/namespace/'})
                self.assertEqual(result, 'http://localhost:3000,foohost:3001/namespace/')

                result = serialize({'protocol': 'http', 'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001]})
                self.assertEqual(result, 'http://localhost:3000,foohost:3001/')

                result = serialize({'protocol': 'https', 'hosts': ['localhost', 'foohost'], 'ports': [3000, 3001]})
                self.assertEqual(result, 'https://localhost:3000,foohost:3001/')

                result = serialize({'protocol': 'foo', 'hosts': ['ds143144-a0.mlab.com', 'ds143144-a1.mlab.com'], 'ports': [43144, 43145], 'auth': 'm+4.gTe~5e^(:m+4.gTe~5e^(', 'path': '/bar-baz'})
                self.assertEqual(result, 'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144,ds143144-a1.mlab.com:43145/bar-baz')

    def test_deserialize(self):
        for deserialize_function in ['deserialize', 'unpack', 'parse']:
            self.assertTrue(hasattr(uri, deserialize_function))

            deserialize = getattr(uri, deserialize_function)

            self.assertTrue(callable(deserialize))

            with self.assertNotRaises(uri.Error):

                username = 'AZaz09+,/='
                password = ''.join(reversed(username))
                credentials = {
                    'username': 'AZaz09+,/=',
                    'password': password,
                }

                # no args

                result = deserialize(None)
                self.assertDeepEqual(result, None)

                # begins with `path`

                result = deserialize('/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('/namespace')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80/namespace',
                    'urls': [
                        'http://localhost:80/namespace'
                    ],
                })

                result = deserialize('/namespace/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80/namespace/',
                    'urls': [
                        'http://localhost:80/namespace/'
                    ],
                })

                result = deserialize('/namespace/foo')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80/namespace/foo',
                    'urls': [
                        'http://localhost:80/namespace/foo'
                    ],
                })

                result = deserialize('/namespace/foo/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80/namespace/foo/',
                    'urls': [
                        'http://localhost:80/namespace/foo/'
                    ],
                })

                result = deserialize('/localhost/namespace')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/localhost/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'localhost/namespace',
                    'namespace': 'localhost/namespace',

                    'url': 'http://localhost:80/localhost/namespace',
                    'urls': [
                        'http://localhost:80/localhost/namespace'
                    ],
                })

                result = deserialize('/localhost/namespace/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/localhost/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'localhost/namespace',
                    'namespace': 'localhost/namespace',

                    'url': 'http://localhost:80/localhost/namespace/',
                    'urls': [
                        'http://localhost:80/localhost/namespace/'
                    ],
                })

                # begins with `host`

                result = deserialize('localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('localhost/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('localhost:3000')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000/',
                    'urls': [
                        'http://localhost:3000/'
                    ],
                })

                result = deserialize('localhost:3000/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000/',
                    'urls': [
                        'http://localhost:3000/'
                    ],
                })

                result = deserialize('localhost/namespace')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80/namespace',
                    'urls': [
                        'http://localhost:80/namespace'
                    ],
                })

                result = deserialize('localhost/namespace/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80/namespace/',
                    'urls': [
                        'http://localhost:80/namespace/'
                    ],
                })

                result = deserialize('localhost/namespace/foo')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80/namespace/foo',
                    'urls': [
                        'http://localhost:80/namespace/foo'
                    ],
                })

                result = deserialize('localhost/namespace/foo/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80/namespace/foo/',
                    'urls': [
                        'http://localhost:80/namespace/foo/'
                    ],
                })

                result = deserialize('localhost:3000/namespace')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:3000/namespace',
                    'urls': [
                        'http://localhost:3000/namespace'
                    ],
                })

                result = deserialize('localhost:3000/namespace/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:3000/namespace/',
                    'urls': [
                        'http://localhost:3000/namespace/'
                    ],
                })

                result = deserialize('localhost:3000/namespace/foo')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:3000/namespace/foo',
                    'urls': [
                        'http://localhost:3000/namespace/foo'
                    ],
                })

                result = deserialize('localhost:3000/namespace/foo/')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:3000/namespace/foo/',
                    'urls': [
                        'http://localhost:3000/namespace/foo/'
                    ],
                })

                # begins with `host` - multiple hosts

                result = deserialize('localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('localhost,foohost/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000,foohost:4000/',
                    'urls': [
                        'http://localhost:3000/',
                        'http://foohost:4000/'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000,foohost:4000/',
                    'urls': [
                        'http://localhost:3000/',
                        'http://foohost:4000/'
                    ],
                })

                result = deserialize('localhost,foohost/namespace')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80,foohost:80/namespace',
                    'urls': [
                        'http://localhost:80/namespace',
                        'http://foohost:80/namespace'
                    ],
                })

                result = deserialize('localhost,foohost/namespace/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:80,foohost:80/namespace/',
                    'urls': [
                        'http://localhost:80/namespace/',
                        'http://foohost:80/namespace/'
                    ],
                })

                result = deserialize('localhost,foohost/namespace/foo')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80,foohost:80/namespace/foo',
                    'urls': [
                        'http://localhost:80/namespace/foo',
                        'http://foohost:80/namespace/foo'
                    ],
                })

                result = deserialize('localhost,foohost/namespace/foo/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:80,foohost:80/namespace/foo/',
                    'urls': [
                        'http://localhost:80/namespace/foo/',
                        'http://foohost:80/namespace/foo/'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000/namespace')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:3000,foohost:4000/namespace',
                    'urls': [
                        'http://localhost:3000/namespace',
                        'http://foohost:4000/namespace'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000/namespace/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'http://localhost:3000,foohost:4000/namespace/',
                    'urls': [
                        'http://localhost:3000/namespace/',
                        'http://foohost:4000/namespace/'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000/namespace/foo')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:3000,foohost:4000/namespace/foo',
                    'urls': [
                        'http://localhost:3000/namespace/foo',
                        'http://foohost:4000/namespace/foo'
                    ],
                })

                result = deserialize('localhost:3000,foohost:4000/namespace/foo/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'http://localhost:3000,foohost:4000/namespace/foo/',
                    'urls': [
                        'http://localhost:3000/namespace/foo/',
                        'http://foohost:4000/namespace/foo/'
                    ],
                })

                # begins with `auth`

                result = deserialize('@localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize(':@localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('{username}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('{username}:@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials)
                    ],
                })

                result = deserialize(':{password}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': ':{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://:{password}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://:{password}@localhost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('{username}:{password}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}:{password}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}:{password}@localhost:80/'.format(**credentials)
                    ],
                })

                # begins with `auth` - multiple hosts

                result = deserialize('@localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize(':@localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('{username}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials),
                        'http://{username}@foohost:80/'.format(**credentials),
                    ],
                })

                result = deserialize('{username}:@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials),
                        'http://{username}@foohost:80/'.format(**credentials)
                    ],
                })

                result = deserialize(':{password}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': ':{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://:{password}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://:{password}@localhost:80/'.format(**credentials),
                        'http://:{password}@foohost:80/'.format(**credentials)
                    ]
                })

                result = deserialize('{username}:{password}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}:{password}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}:{password}@localhost:80/'.format(**credentials),
                        'http://{username}:{password}@foohost:80/'.format(**credentials)
                    ],
                })

                # begins with `protocol`

                result = deserialize('http://localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('http://localhost/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('http://localhost:3000')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000/',
                    'urls': [
                        'http://localhost:3000/'
                    ],
                })

                result = deserialize('http://localhost:3000/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000/',
                    'urls': [
                        'http://localhost:3000/'
                    ],
                })

                result = deserialize('https://localhost:3000')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,
                    'namespace': None,

                    'url': 'https://localhost:3000/',
                    'urls': [
                        'https://localhost:3000/'
                    ],
                })

                result = deserialize('https://localhost:3000/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'https://localhost:3000/',
                    'urls': [
                        'https://localhost:3000/'
                    ],
                })

                result = deserialize('https://localhost:3000/namespace')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'https://localhost:3000/namespace',
                    'urls': [
                        'https://localhost:3000/namespace'
                    ],
                })

                result = deserialize('https://localhost:3000/namespace/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'https://localhost:3000/namespace/',
                    'urls': [
                        'https://localhost:3000/namespace/'
                    ],
                })

                result = deserialize('https://localhost:3000/namespace/foo')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'https://localhost:3000/namespace/foo',
                    'urls': [
                        'https://localhost:3000/namespace/foo'
                    ],
                })

                result = deserialize('https://localhost:3000/namespace/foo/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 3000,
                    'ports': [3000],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'https://localhost:3000/namespace/foo/',
                    'urls': [
                        'https://localhost:3000/namespace/foo/'
                    ],
                })

                result = deserialize('http://@localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('http://:@localhost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80/',
                    'urls': [
                        'http://localhost:80/'
                    ],
                })

                result = deserialize('http://{username}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials)
                    ]
                })

                result = deserialize('http://{username}:@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials)
                    ]
                })

                result = deserialize('http://:{password}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': ':{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://:{password}@localhost:80/'.format(**credentials),
                    'urls':[
                        'http://:{password}@localhost:80/'.format(**credentials)
                    ]
                })

                result = deserialize('http://{username}:{password}@localhost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost'],

                    'port': 80,
                    'ports': [80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}:{password}@localhost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}:{password}@localhost:80/'.format(**credentials)
                    ]
                })

                result = deserialize('foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144/bar-baz')
                self.assertDeepEqual(result, {
                    'protocol': 'foo',
                    'auth': 'm+4.gTe~5e^(:m+4.gTe~5e^(',

                    'endpoint': 'ds143144-a0.mlab.com:43144',
                    'endpoints': ['ds143144-a0.mlab.com:43144'],

                    'host': 'ds143144-a0.mlab.com',
                    'hosts': ['ds143144-a0.mlab.com'],

                    'port': 43144,
                    'ports': [43144],

                    'path': '/bar-baz',
                    'query': {},

                    'credentials': {
                        'username': 'm+4.gTe~5e^(',
                        'password': 'm+4.gTe~5e^(',
                    },
                    'key': 'bar-baz',
                    'namespace': 'bar-baz',

                    'url': 'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144/bar-baz',
                    'urls': [
                        'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144/bar-baz'
                    ]
                })

                # begins with `protocol` - multiple hosts

                result = deserialize('http://localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/',
                    ],
                })

                result = deserialize('http://localhost,foohost/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('http://localhost:3000,foohost:4000')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000,foohost:4000/',
                    'urls': [
                        'http://localhost:3000/',
                        'http://foohost:4000/',
                    ],
                })

                result = deserialize('http://localhost:3000,foohost:4000/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:3000,foohost:4000/',
                    'urls': [
                        'http://localhost:3000/',
                        'http://foohost:4000/'
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'https://localhost:3000,foohost:4000/',
                    'urls': [
                        'https://localhost:3000/',
                        'https://foohost:4000/',
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'https://localhost:3000,foohost:4000/',
                    'urls': [
                        'https://localhost:3000/',
                        'https://foohost:4000/'
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000/namespace')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'https://localhost:3000,foohost:4000/namespace',
                    'urls': [
                        'https://localhost:3000/namespace',
                        'https://foohost:4000/namespace'
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000/namespace/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace',
                    'namespace': 'namespace',

                    'url': 'https://localhost:3000,foohost:4000/namespace/',
                    'urls': [
                        'https://localhost:3000/namespace/',
                        'https://foohost:4000/namespace/'
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000/namespace/foo')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/foo',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'https://localhost:3000,foohost:4000/namespace/foo',
                    'urls': [
                        'https://localhost:3000/namespace/foo',
                        'https://foohost:4000/namespace/foo'
                    ],
                })

                result = deserialize('https://localhost:3000,foohost:4000/namespace/foo/')
                self.assertDeepEqual(result,
                    {
                    'protocol': 'https',
                    'auth': None,

                    'endpoint': 'localhost:3000',
                    'endpoints': ['localhost:3000', 'foohost:4000'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 3000,
                    'ports': [3000, 4000],

                    'path': '/namespace/foo/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': 'namespace/foo',
                    'namespace': 'namespace/foo',

                    'url': 'https://localhost:3000,foohost:4000/namespace/foo/',
                    'urls': [
                        'https://localhost:3000/namespace/foo/',
                        'https://foohost:4000/namespace/foo/'
                    ],
                })

                result = deserialize('http://@localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('http://:@localhost,foohost')
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': None,

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://localhost:80,foohost:80/',
                    'urls': [
                        'http://localhost:80/',
                        'http://foohost:80/'
                    ],
                })

                result = deserialize('http://{username}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials),
                        'http://{username}@foohost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('http://{username}:@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': None,
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}@localhost:80/'.format(**credentials),
                        'http://{username}@foohost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('http://:{password}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': ':{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': None,
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://:{password}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://:{password}@localhost:80/'.format(**credentials),
                        'http://:{password}@foohost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('http://{username}:{password}@localhost,foohost'.format(**credentials))
                self.assertDeepEqual(result, {
                    'protocol': 'http',
                    'auth': '{username}:{password}'.format(**credentials),

                    'endpoint': 'localhost:80',
                    'endpoints': ['localhost:80', 'foohost:80'],

                    'host': 'localhost',
                    'hosts': ['localhost', 'foohost'],

                    'port': 80,
                    'ports': [80, 80],

                    'path': '/',
                    'query': {},

                    'credentials': {
                        'username': credentials['username'],
                        'password': credentials['password'],
                    },
                    'key': None,
                    'namespace': None,

                    'url': 'http://{username}:{password}@localhost:80,foohost:80/'.format(**credentials),
                    'urls': [
                        'http://{username}:{password}@localhost:80/'.format(**credentials),
                        'http://{username}:{password}@foohost:80/'.format(**credentials)
                    ],
                })

                result = deserialize('foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144,ds143144-a1.mlab.com:43145/bar-baz')
                self.assertDeepEqual(result, {
                    'protocol': 'foo',
                    'auth': 'm+4.gTe~5e^(:m+4.gTe~5e^(',

                    'host': 'ds143144-a0.mlab.com',
                    'port': 43144,

                    'endpoint': 'ds143144-a0.mlab.com:43144',
                    'endpoints': ['ds143144-a0.mlab.com:43144', 'ds143144-a1.mlab.com:43145'],

                    'host': 'ds143144-a0.mlab.com',
                    'hosts': ['ds143144-a0.mlab.com', 'ds143144-a1.mlab.com'],

                    'port': 43144,
                    'ports': [43144, 43145],

                    'path': '/bar-baz',
                    'query': {},

                    'credentials': {
                        'username': 'm+4.gTe~5e^(',
                        'password': 'm+4.gTe~5e^(',
                    },
                    'key': 'bar-baz',
                    'namespace': 'bar-baz',

                    'url': 'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144,ds143144-a1.mlab.com:43145/bar-baz',
                    'urls': [
                        'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a0.mlab.com:43144/bar-baz',
                        'foo://m+4.gTe~5e^(:m+4.gTe~5e^(@ds143144-a1.mlab.com:43145/bar-baz'
                    ],
                })

    def test_pack(self):
        self.assertTrue(hasattr(uri, 'pack'))
        self.assertTrue(callable(uri.pack))

        # @see `test_serialize`

    def test_unpack(self):
        self.assertTrue(hasattr(uri, 'unpack'))
        self.assertTrue(callable(uri.unpack))

        # @see `test_deserialize`

    def test_stringify(self):
        self.assertTrue(hasattr(uri, 'stringify'))
        self.assertTrue(callable(uri.stringify))

        # @see `test_serialize`

    def test_parse(self):
        self.assertTrue(hasattr(uri, 'parse'))
        self.assertTrue(callable(uri.parse))

        # @see `test_deserialize`

    def test_get(self):
        self.assertTrue(hasattr(uri, 'get'))
        self.assertTrue(callable(uri.get))

        with self.assertNotRaises(Exception):
            result = uri.get(None)
            self.assertEqual(result, None)

            result = uri.get('/')
            self.assertEqual(result, 'http://localhost:80/')

            result = uri.get('localhost')
            self.assertEqual(result, 'http://localhost:80/')

            result = uri.get('localhost/')
            self.assertEqual(result, 'http://localhost:80/')

            result = uri.get('localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('https://localhost:3000')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('https://localhost:3000/')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('/namespace')
            self.assertEqual(result, 'http://localhost:80/namespace')

            result = uri.get('/namespace/')
            self.assertEqual(result, 'http://localhost:80/namespace/')

            result = uri.get('localhost/namespace')
            self.assertEqual(result, 'http://localhost:80/namespace')

            result = uri.get('localhost/namespace/')
            self.assertEqual(result, 'http://localhost:80/namespace/')

            result = uri.get('/localhost/namespace')
            self.assertEqual(result, 'http://localhost:80/localhost/namespace')

            result = uri.get('/localhost/namespace/')
            self.assertEqual(result, 'http://localhost:80/localhost/namespace/')

            result = uri.get('localhost:3000/namespace')
            self.assertEqual(result, 'http://localhost:3000/namespace')

            result = uri.get('localhost:3000/namespace/')
            self.assertEqual(result, 'http://localhost:3000/namespace/')

            result = uri.get('http://localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('https://localhost:3000')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('https://localhost:3000/')
            self.assertEqual(result, 'https://localhost:3000/')

            # multiple hosts

            result = uri.get('localhost')
            self.assertEqual(result, 'http://localhost:80/')

            result = uri.get('localhost/')
            self.assertEqual(result, 'http://localhost:80/')

            result = uri.get('localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('https://localhost:3000')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('https://localhost:3000/')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('localhost/namespace')
            self.assertEqual(result, 'http://localhost:80/namespace')

            result = uri.get('localhost/namespace/')
            self.assertEqual(result, 'http://localhost:80/namespace/')

            result = uri.get('localhost:3000/namespace')
            self.assertEqual(result, 'http://localhost:3000/namespace')

            result = uri.get('localhost:3000/namespace/')
            self.assertEqual(result, 'http://localhost:3000/namespace/')

            result = uri.get('http://localhost:3000')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('http://localhost:3000/')
            self.assertEqual(result, 'http://localhost:3000/')

            result = uri.get('https://localhost:3000')
            self.assertEqual(result, 'https://localhost:3000/')

            result = uri.get('https://localhost:3000/')
            self.assertEqual(result, 'https://localhost:3000/')

    def test_test(self):
        self.assertTrue(hasattr(uri, 'test'))
        self.assertTrue(callable(uri.test))

        data = None

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = 'eyJmb28iOiBbMSwgMiwgM119'

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = {}

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = {
            'a1': {
                'b1': {
                    'c1': [1, 2, 3],
                    'c2': 100
                }
            },
            'a2': True,
        }

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = {
            'a1.b1.c1': [1, 2, 3],
            'a1.b1.c2': 100,
            'a2': True,
        }

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = '{"foo":[1,2,3]}'

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = '[{"foo":[1,2,3]}]'

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = '\x81\xa3foo\x93\x01\x02\x03'

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        data = 'foo:\n- 1\n- 2\n- 3'

        with self.assertNotRaises(uri.Error):
            result = uri.test(data)

        self.assertEqual(result, False)

        # NOTE: `uri` case more verbose
        with self.assertNotRaises(uri.Error):
            result = uri.test('/')
            self.assertEqual(result, False)

            result = uri.test('localhost')
            self.assertEqual(result, False)

            result = uri.test('localhost/')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/')
            self.assertEqual(result, False)

            result = uri.test('http://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('/namespace')
            self.assertEqual(result, False)

            result = uri.test('/namespace/')
            self.assertEqual(result, False)

            result = uri.test('localhost/namespace')
            self.assertEqual(result, False)

            result = uri.test('localhost/namespace/')
            self.assertEqual(result, False)

            result = uri.test('/localhost/namespace')
            self.assertEqual(result, False)

            result = uri.test('/localhost/namespace/')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/namespace')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/namespace/')
            self.assertEqual(result, False)

            result = uri.test('http://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/namespace')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/namespace')
            self.assertEqual(result, True)

            # multiple hosts

            result = uri.test('localhost')
            self.assertEqual(result, False)

            result = uri.test('localhost/')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/')
            self.assertEqual(result, False)

            result = uri.test('http://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('localhost/namespace')
            self.assertEqual(result, False)

            result = uri.test('localhost/namespace/')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/namespace')
            self.assertEqual(result, False)

            result = uri.test('localhost:3000/namespace/')
            self.assertEqual(result, False)

            result = uri.test('http://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('http://localhost:3000/namespace')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/')
            self.assertEqual(result, True)

            result = uri.test('https://localhost:3000/namespace')
            self.assertEqual(result, True)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
