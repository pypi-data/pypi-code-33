import unittest
from opentmi_client.utils.Base import BaseApi


class TestBase(unittest.TestCase):
    def test_basics(self):
        base = BaseApi()
        self.assertEqual(base.data, {})
        self.assertEqual(str(base), '{}')
        self.assertTrue(base.is_empty)

    def test_id(self):
        base = BaseApi()
        base._id = "abc"
        self.assertEqual(base.data, {"_id": "abc"})
        self.assertEqual(str(base), '{\n  "_id": "abc"\n}')
        self.assertFalse(base.is_empty)

    def test_set(self):
        base = BaseApi()
        base.set('a', 1)
        self.assertEqual(base.data, {'a': 1})
        self.assertEqual(str(base), '{\n  "a": 1\n}')
        self.assertFalse(base.is_empty)
        self.assertEqual(base.get('a'), 1)

    def test_unset(self):
        base = BaseApi()
        base.set('a', 1)
        base.unset('a')
        self.assertTrue(base.is_empty)

    def test_nested(self):
        base = BaseApi()
        base.set('a.b.c', 2)
        self.assertEqual(base.data, {'a': {'b': {'c': 2}}})
        self.assertEqual(str(base), '{\n  "a": {\n    "b": {\n      "c": 2\n    }\n  }\n}')
        self.assertEqual(base.get('a.b.c'), 2)

    def test_subclass(self):
        base = BaseApi()
        class Test(BaseApi):
            pass
        base.set('a.b', Test())
        base.set('b', 'b')
        self.assertEqual(base.data, {'b': 'b'})
        self.assertEqual(str(base), '{\n  "b": "b"\n}')
        self.assertFalse(base.is_empty)

    def test_set_data_key_not_exists(self):
        base = BaseApi()
        with self.assertRaises(KeyError):
            base.data = {"a": "a"}

    def test_set_data_key_exists(self):
        class A(BaseApi):
            @property
            def a(self):
                return self.get("a")
            @a.setter
            def a(self, value):
                self.set("a", value)

        base = A()
        base.data = {"a": "a"}
        self.assertEqual(base.data, {"a": "a"})
        self.assertEqual(base.a, "a")

    def test_set_data_nested_key_not_exists(self):
        class A(BaseApi):
            @property
            def a(self):
                return self.get("a")
            @a.setter
            def a(self, value):
                self.set("a", value)

        base = A()
        with self.assertRaises(KeyError):
            base.data = {"a": {"a": 1}}

    def test_set_data_nested_key_exists(self):
        class InnerA(BaseApi):
            @property
            def a(self):
                return self.get("a")
            @a.setter
            def a(self, value):
                self.set("a", value)

        class A(BaseApi):
            def __init__(self):
                super(A, self).__init__()
                self.a = InnerA()
            @property
            def a(self):
                return self.get("a")
            @a.setter
            def a(self, value):
                self.set("a", value)

        base = A()
        base.data = {"a": {"a": 1}}
        self.assertEqual(base.data, {"a": {"a": 1}})
        self.assertEqual(base.a, {"a": 1})

    def test_set_data_empty(self):
        base = BaseApi()
        base.data = {}
        self.assertEqual(base.data, {})
