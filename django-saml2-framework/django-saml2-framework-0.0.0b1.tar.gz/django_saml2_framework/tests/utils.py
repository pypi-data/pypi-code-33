from django.test import TestCase

from ..utils import deepmerge


class DeepCopyTestCase(TestCase):
    def setUp(self):
        pass

    def test_simple_merge(self):
        a = {'a': 1}
        b = {'b': 2}
        deepmerge(a, b)
        self.assertEqual(a, {'a': 1, 'b': 2})

    def test_complex_merge(self):
        a = {'a': 1, 'c': {'1': 'a1'}}
        b = {'b': 2, 'c': {'2': 'b2'}}
        deepmerge(a, b)
        self.assertEqual(a, {'a': 1, 'b': 2, 'c': {'1': 'a1', '2': 'b2'}})
