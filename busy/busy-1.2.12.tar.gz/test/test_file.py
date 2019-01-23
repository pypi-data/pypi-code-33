from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory

from busy.plugins.todo import TodoQueue
from busy.plugins.todo import PlanQueue
from busy.queue import Queue
from busy.plugins.todo import Task
from busy.file import File
from busy.item import Item

class TestFile(TestCase):

    def test_load_items(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'x.txt'
            p.write_text('a\nb\n')
            f = File(p)
            q = f.queue
            self.assertIsInstance(q, Queue)
            self.assertEqual(str(q.get()), 'a')
            self.assertIsInstance(q.get(), Item)

    def test_load_if_not_there(self):
        with TemporaryDirectory() as d:
            f = File(Path(d) / 'y.txt')
            q = f.queue
            self.assertIsInstance(q, Queue)
            self.assertEqual(q.count(), 0)

    def test_save_items(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'z.txt'
            f1 = File(p)
            q1 = f1.queue
            q1.add(Item('a'))
            f1.save()
            f2 = File(p)
            q2 = f2.queue
            self.assertEqual(str(q2.get()), 'a')

    def test_plan_file_format(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'plans.txt'
            p.write_text('2018-12-01|a\n2018-12-09|b')
            q = File(p, PlanQueue).queue
            self.assertEqual(q.get().date.month, 12)
