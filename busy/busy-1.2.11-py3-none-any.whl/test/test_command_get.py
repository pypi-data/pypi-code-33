from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import mock
from io import StringIO
from datetime import date as Date

from busy.plugins.todo import Task
from busy.commander import Commander

class TestCommandGet(TestCase):

    def test_get(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a\nb\nc\nd')
            c = Commander(root=t)
            o = c.handle('get')
            self.assertEqual(o, 'a')

    def test_get_if_no_tasks(self):
        with TemporaryDirectory() as t:
            c = Commander(root=t)
            o = c.handle('get')
            self.assertEqual(o, '')

    def test_get_with_criteria(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a\nb\nc\nd')
            c = Commander(root=t)
            with self.assertRaises(RuntimeError):
                c.handle('get','3-4')
