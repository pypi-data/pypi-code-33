# -*- coding: utf-8 -*-
from mock import sentinel, ANY

import odooly
from ._common import XmlRpcTestCase, OBJ

ID1, ID2 = 4001, 4002


def _skip_test(test_case):
    pass


class IdentDict(object):
    def __init__(self, _id):
        self._id = _id

    def __repr__(self):
        return 'IdentDict(%s)' % (self._id,)

    def __getitem__(self, key):
        return (key == 'id') and self._id or ('v_%s_%s' % (key, self._id))

    def __eq__(self, other):
        return self._id == other._id
DIC1 = IdentDict(ID1)
DIC2 = IdentDict(ID2)


class TestOdooApi(XmlRpcTestCase):
    """Test the Client API."""
    server_version = '6.1'
    server = 'http://127.0.0.1:8069'
    database = 'database'
    user = 'user'
    password = 'passwd'
    uid = 1

    def obj_exec(self, *args):
        if args[4] == 'search':
            return [ID2, ID1]
        if args[4] == 'read':
            return [IdentDict(res_id) for res_id in args[5][0][::-1]]
        return sentinel.OTHER

    def setUp(self):
        super(TestOdooApi, self).setUp()
        self.service.object.execute_kw.side_effect = self.obj_exec
        # preload 'foo.bar'
        self.env._get('foo.bar', False)
        self.service.reset_mock()

    def test_search(self):
        search = self.env['foo.bar'].search

        searchterm = 'name like Morice'
        self.assertEqual(search([searchterm]).id, [ID2, ID1])
        self.assertEqual(search([searchterm], limit=2).id, [ID2, ID1])
        self.assertEqual(search([searchterm], offset=80, limit=99),
                         odooly.RecordList(self.env['foo.bar'], [ID2, ID1]))
        self.assertEqual(search([searchterm], order='name ASC').id,
                         [ID2, ID1])
        search(['name = mushroom', 'state != draft'])
        search([('name', 'like', 'Morice')])
        self.env.execute('foo.bar', 'search', [('name like Morice')])
        search([])
        domain = [('name', 'like', 'Morice')]
        domain2 = [('name', '=', 'mushroom'), ('state', '!=', 'draft')]
        self.assertCalls(
            OBJ('foo.bar', 'search', domain),
            OBJ('foo.bar', 'search', domain, 0, 2, None),
            OBJ('foo.bar', 'search', domain, 80, 99, None),
            OBJ('foo.bar', 'search', domain, 0, None, 'name ASC'),
            OBJ('foo.bar', 'search', domain2),
            OBJ('foo.bar', 'search', domain),
            OBJ('foo.bar', 'search', domain),
            OBJ('foo.bar', 'search', []),
        )
        self.assertOutput('')

        # Not supported
        search('name like Morice')
        self.assertCalls(OBJ('foo.bar', 'search', 'name like Morice'))

        search(['name like Morice'], missingkey=42)
        self.assertCalls(OBJ('foo.bar', 'search', domain, missingkey=42))
        self.assertOutput('')

        self.assertRaises(TypeError, search)
        self.assertRaises(ValueError, search, ['abc'])
        self.assertRaises(ValueError, search, ['< id'])
        self.assertRaises(ValueError, search, ['name Morice'])

        self.assertCalls()
        self.assertOutput('')

    def test_count(self):
        count = self.env['foo.bar'].search_count

        count(['name like Morice'])
        count(['name = mushroom', 'state != draft'])
        count([('name', 'like', 'Morice')])
        self.env.execute('foo.bar', 'search_count', [('name like Morice')])
        count([])
        count()
        domain = [('name', 'like', 'Morice')]
        domain2 = [('name', '=', 'mushroom'), ('state', '!=', 'draft')]
        self.assertCalls(
            OBJ('foo.bar', 'search_count', domain),
            OBJ('foo.bar', 'search_count', domain2),
            OBJ('foo.bar', 'search_count', domain),
            OBJ('foo.bar', 'search_count', domain),
            OBJ('foo.bar', 'search_count', []),
            OBJ('foo.bar', 'search_count', []),
        )
        self.assertOutput('')

        # Not supported
        count('name like Morice')
        self.assertCalls(OBJ('foo.bar', 'search_count', 'name like Morice'))

        self.assertRaises(TypeError, count,
                          ['name like Morice'], limit=2)
        self.assertRaises(TypeError, count,
                          ['name like Morice'], offset=80, limit=99)
        self.assertRaises(TypeError, count,
                          ['name like Morice'], order='name ASC')
        self.assertRaises(ValueError, count, ['abc'])
        self.assertRaises(ValueError, count, ['< id'])
        self.assertRaises(ValueError, count, ['name Morice'])

        self.assertCalls()
        self.assertOutput('')

    def test_read_simple(self):
        read = self.env['foo.bar'].read

        read(42)
        read([42])
        read([13, 17])
        read([42], 'first_name')
        self.assertCalls(
            OBJ('foo.bar', 'read', [42]),
            OBJ('foo.bar', 'read', [42]),
            OBJ('foo.bar', 'read', [13, 17]),
            OBJ('foo.bar', 'read', [42], ['first_name']),
        )
        self.assertOutput('')

    def test_read_complex(self):
        read = self.env['foo.bar'].read
        self.service.object.execute_kw.side_effect = self.obj_exec

        searchterm = 'name like Morice'
        self.assertEqual(read([searchterm]), [DIC1, DIC2])
        self.assertEqual(read([searchterm], limit=2), [DIC1, DIC2])
        self.assertEqual(read([searchterm], offset=80, limit=99),
                         [DIC1, DIC2])
        self.assertEqual(read([searchterm], order='name ASC'),
                         [DIC2, DIC1])
        read([searchterm], 'birthdate city')
        read([searchterm], 'birthdate city', limit=2)
        read([searchterm], limit=2, fields=['birthdate', 'city'])
        read([searchterm], order='name ASC')
        read(['name = mushroom', 'state != draft'])
        read([('name', 'like', 'Morice')])
        self.env.execute('foo.bar', 'read', ['name like Morice'])

        rv = read(['name like Morice'],
                  'aaa %(birthdate)s bbb %(city)s', offset=80, limit=99)
        self.assertEqual(rv, ['aaa v_birthdate_4001 bbb v_city_4001',
                              'aaa v_birthdate_4002 bbb v_city_4002'])

        def call_read(*args, **kw):
            return OBJ('foo.bar', 'read', [ID2, ID1], *args, **kw)
        domain = [('name', 'like', 'Morice')]
        domain2 = [('name', '=', 'mushroom'), ('state', '!=', 'draft')]
        self.assertCalls(
            OBJ('foo.bar', 'search', domain), call_read(),
            OBJ('foo.bar', 'search', domain, 0, 2, None), call_read(),
            OBJ('foo.bar', 'search', domain, 80, 99, None), call_read(),
            OBJ('foo.bar', 'search', domain, 0, None, 'name ASC'),
            call_read(),
            OBJ('foo.bar', 'search', domain), call_read(['birthdate', 'city']),
            OBJ('foo.bar', 'search', domain, 0, 2, None),
            call_read(['birthdate', 'city']),
            OBJ('foo.bar', 'search', domain, 0, 2, None),
            call_read(fields=['birthdate', 'city']),
            OBJ('foo.bar', 'search', domain, 0, None, 'name ASC'),
            call_read(),
            OBJ('foo.bar', 'search', domain2), call_read(),
            OBJ('foo.bar', 'search', domain), call_read(),
            OBJ('foo.bar', 'search', domain), call_read(),
            OBJ('foo.bar', 'search', domain, 80, 99, None),
            call_read(['birthdate', 'city']),
        )
        self.assertOutput('')

    def test_read_false(self):
        read = self.env['foo.bar'].read

        self.assertEqual(read(False), False)

        self.assertEqual(read([False]), [])
        self.assertEqual(read([False, False]), [])
        self.assertEqual(read([False], 'first_name'), [])
        self.assertEqual(read([False], order=True),
                         [False])
        self.assertEqual(read([False, False], order=True),
                         [False, False])
        self.assertEqual(read([False], 'first_name', order=True),
                         [False])
        self.assertEqual(read([], 'first_name'), [])
        self.assertEqual(read([], 'first_name', order=True), [])

        self.assertCalls()

        self.assertEqual(read([False, 42]), [IdentDict(42)])
        self.assertEqual(read([False, 13, 17, False]),
                         [IdentDict(17), IdentDict(13)])
        self.assertEqual(read([13, False, 17], 'first_name'),
                         ['v_first_name_17', 'v_first_name_13'])
        self.assertEqual(read([False, 42], order=True),
                         [False, IdentDict(42)])
        self.assertEqual(read([False, 13, 17, False], order=True),
                         [False, IdentDict(13), IdentDict(17), False])
        self.assertEqual(read([13, False, 17], 'city', order=True),
                         ['v_city_13', False, 'v_city_17'])

        self.assertCalls(
            OBJ('foo.bar', 'read', [42]),
            OBJ('foo.bar', 'read', [13, 17]),
            OBJ('foo.bar', 'read', [13, 17], ['first_name']),
            OBJ('foo.bar', 'read', [42]),
            OBJ('foo.bar', 'read', [13, 17]),
            OBJ('foo.bar', 'read', [13, 17], ['city']),
        )
        self.assertOutput('')

    def test_read_invalid(self):
        read = self.env['foo.bar'].read
        domain = [('name', 'like', 'Morice')]

        # Not supported
        read('name like Morice')

        read(['name like Morice'], missingkey=42)

        self.assertCalls(
            OBJ('foo.bar', 'read', ['name like Morice']),
            OBJ('foo.bar', 'search', domain),
            OBJ('foo.bar', 'read', ANY, missingkey=42))
        self.assertOutput('')

        self.assertRaises(AssertionError, read)
        self.assertRaises(ValueError, read, ['abc'])
        self.assertRaises(ValueError, read, ['< id'])
        self.assertRaises(ValueError, read, ['name Morice'])

        self.assertCalls()
        self.assertOutput('')

    def test_method(self, method_name='method', single_id=True):
        method = getattr(self.env['foo.bar'], method_name)

        single_id = single_id and 42 or [42]

        method(42)
        method([42])
        method([13, 17])
        self.env.execute('foo.bar', method_name, [42])
        method([])
        self.assertCalls(
            OBJ('foo.bar', method_name, single_id),
            OBJ('foo.bar', method_name, [42]),
            OBJ('foo.bar', method_name, [13, 17]),
            OBJ('foo.bar', method_name, [42]),
            OBJ('foo.bar', method_name, []),
        )
        self.assertOutput('')

    def test_standard_methods(self):
        for method in 'write', 'copy', 'unlink', 'get_metadata':
            self.test_method(method)

        # self.test_method('get_metadata', single_id=False)

    def test_keys(self):
        self.service.object.execute_kw.side_effect = [['spam']]
        self.assertTrue(self.env['foo.bar'].keys())
        self.assertCalls(
            OBJ('foo.bar', 'fields_get_keys'),
        )
        self.assertOutput('')

    def test_fields(self):
        self.service.object.execute_kw.side_effect = [{'spam': sentinel.FIELD}]
        self.assertTrue(self.env['foo.bar'].fields())
        self.assertCalls(
            OBJ('foo.bar', 'fields_get'),
        )
        self.assertOutput('')

    def test_field(self):
        self.service.object.execute_kw.side_effect = [{'spam': sentinel.FIELD}]
        self.assertTrue(self.env['foo.bar'].field('spam'))

        self.assertRaises(TypeError, self.env['foo.bar'].field)
        self.assertCalls(
            OBJ('foo.bar', 'fields_get'),
        )
        self.assertOutput('')


class TestOdooApi90(TestOdooApi):
    """Test the Client API for Odoo 9."""
    server_version = '9.0'


class TestOdooApi11(TestOdooApi):
    """Test the Client API for Odoo 11."""
    server_version = '11.0'
