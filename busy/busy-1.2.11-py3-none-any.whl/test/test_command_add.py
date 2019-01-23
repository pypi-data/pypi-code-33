from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import mock
from io import StringIO
from datetime import date as Date

from busy.plugins.todo import Task
from busy.commander import Commander

class TestCommandAdd(TestCase):

    def test_by_parameter(self):
        with TemporaryDirectory() as t:
            c = Commander(root=t)
            c.handle('add','u p')
            x = Path(t, 'tasks.txt').read_text()
            self.assertEqual(x, 'u p\n')

    def test_add_by_input(self):
        with TemporaryDirectory() as t:
            c = Commander(root=t)
            with mock.patch('sys.stdin', StringIO('g')):
                c.handle('add')
                x = Path(t, 'tasks.txt').read_text()
                self.assertEqual(x, 'g\n')
