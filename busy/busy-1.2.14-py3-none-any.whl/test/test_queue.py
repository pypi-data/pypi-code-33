from unittest import TestCase
import unittest

from busy.queue import Queue

class TestQueue(TestCase):

    def test_list(self):
        q = Queue()
        q.add('a')
        q.add('b')
        i = q.list()
        self.assertEqual(i[0][0], 1)
        self.assertEqual(str(i[0][1]), 'a')

    def test_list_with_criteria(self):
        q = Queue()
        q.add('a','b','c')
        i = q.list(1,3)
        self.assertEqual(i[1][0], 3)
        self.assertEqual(str(i[1][1]), 'c')

    def test_select_multiple(self):
        q = Queue()
        q.add('a','b','c')
        t = q.select(1,3)
        self.assertEqual(len(t), 2)

    def test_pop_multiple(self):
        q = Queue()
        q.add('a','b','c','d')
        q.pop(2,4)
        self.assertEqual(str(q.get(2)), 'd')

    def test_pop_if_nothing(self):
        q = Queue()
        q.pop()
        self.assertEqual(q.count(), 0)

    def test_drop(self):
        q = Queue()
        q.add('a','b','c','d')
        q.drop()
        self.assertEqual(str(q.get(1)), 'b')

    def test_delete(self):
        q = Queue()
        q.add('a','b','c')
        q.delete(2,3)
        self.assertEqual(q.count(), 1)

    def test_create_with_array_of_dict(self):
        q = Queue()
        q.add({'description':'a'})
        self.assertEqual(str(q.get()), 'a')

    def test_list_with_range(self):
        q = Queue()
        q.add('a','b','c')
        t = q.select('2-3')
        self.assertEqual(len(t), 2)

    def test_list_with_range_ending(self):
        q = Queue()
        q.add('a','b','c','d')
        t = q.list('2-')
        self.assertEqual(len(t), 3)
        self.assertEqual(str(t[0][1]), 'b')

    def test_list_only_end(self):
        q = Queue()
        q.add('a','b','c','d')
        t = q.list('-')
        self.assertEqual(len(t), 1)
        self.assertEqual(str(t[0][1]), 'd')

    def test_partial_tags_dont_match(self):
        q = Queue()
        q.add('a #b','b #busy')
        t = q.list('b')
        self.assertEqual(len(t), 1)
