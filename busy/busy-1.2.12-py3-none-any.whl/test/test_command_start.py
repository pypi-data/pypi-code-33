from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import mock
from io import StringIO
from datetime import date as Date

from busy.plugins.todo import Task
from busy.commander import Commander

@mock.patch('busy.editor', lambda x: x)
class TestCommandStart(TestCase):

    def test_start_works_for_named_project(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a\nb #g\nc #k\nd #g')
            c = Commander(root=t)
            o = c.handle('start','g')
            f = p.read_text()
            self.assertEqual(f, 'b #g\nd #g\na\nc #k\n')

    def test_start_fails_if_criteria(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a\nb #g\nc #k\nd #g')
            c = Commander(root=t)
            with self.assertRaises(RuntimeError):
                c.handle('start','g','4')

    def test_start_pops_tasks_for_current_project(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a #k\nb #g\nc #k\nd #g')
            c = Commander(root=t)
            c.handle('start')
            o = p.read_text()
            self.assertEqual(o, 'a #k\nc #k\nb #g\nd #g\n')

    def test_start_activates_today(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'plans.txt')
            p.write_text('2018-09-04|x #g\n2019-03-25|y #g\n')
            c = Commander(root=t)
            with mock.patch('busy.dateparser.today', lambda : Date(2019,2,11)):
                o = c.handle('start','g')
                self.assertEqual(p.read_text(), '2019-03-25|y #g\n')
                p2 = Path(t, 'tasks.txt')
                self.assertEqual(p2.read_text(), 'x #g\n')

    def test_start_fails_gracefully_if_no_todos(self):
        with TemporaryDirectory() as t:
            c = Commander(root=t)
            with self.assertRaises(RuntimeError):
                c.handle('start', 'g')

    def test_start_fails_gracefully_if_no_project_at_top(self):
        with TemporaryDirectory() as t:
            p = Path(t, 'tasks.txt')
            p.write_text('a\nb #g')
            c = Commander(root=t)
            with self.assertRaises(RuntimeError):
                c.handle('start')
