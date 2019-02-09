from unittest import TestCase
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import mock

from busy.plugins.todo import TodoQueue
from busy.root import Root
from busy.file import File

class TestRoot(TestCase):

    def test_root(self):
        with TemporaryDirectory() as d:
            sd = Root(Path(d))
            s = sd.get_queue('tasks')
            self.assertIsInstance(s, TodoQueue)

    def test_add_todo(self):
        with TemporaryDirectory() as td:
            sd1 = Root(Path(td))
            sd1.get_queue('x').add('a')
            sd1.save()
            sd2 = Root(Path(td))
            self.assertEqual(str(sd2.get_queue('x').get()),'a')

    def test_make_dir_pater(self):
        r = Root()
        with TemporaryDirectory() as td:
            r.path = Path(td)
            r.get_queue('y').add('a')
            r.save()
            r2 = Root(Path(td))
            self.assertEqual(str(r2.get_queue('y').get()),'a')

    def test_env_var_as_backup(self):
        with TemporaryDirectory() as td:
            with mock.patch.dict('os.environ', {'BUSY_ROOT': td}):
                sd1 = Root()
                sd1.get_queue('p').add('a')
                sd1.save()
                f = Path(td) / 'p.txt'
                self.assertEqual(f.read_text(),'a\n')

    def test_user_root(self):
        with TemporaryDirectory() as td:
            with mock.patch.dict('os.environ', clear=True):
                with mock.patch('pathlib.Path.home', lambda : Path(td)):
                    sd1 = Root()
                    sd1.get_queue('w').add('a')
                    sd1.save()
                    f = Path(td) / '.busy' / 'w.txt'
                    self.assertEqual(f.read_text(),'a\n')
