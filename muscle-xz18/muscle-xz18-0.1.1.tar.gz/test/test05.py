import io
import sqlite3
import unittest
from pathlib import Path, PosixPath
from unittest.mock import patch

from muscle.controller.controller import Controller
from muscle.model.model import Exercise, Model
from muscle.view.cli import cli


class TestCLI02(unittest.TestCase):

    def setUp(self):
        data_path = Path.home().joinpath(".local/share/muscle/user.db")
        if data_path.exists():
            target = data_path.parent.joinpath("user_backup.db")
            data_path.rename(target)

    def tearDown(self):
        test_data_path = Path.home().joinpath(".local/share/muscle/user.db")
        test_data_path.unlink()
        data_path = Path.home().joinpath(".local/share/muscle/user_backup.db")
        if data_path.exists():
            target = data_path.parent.joinpath("user.db")
            data_path.rename(target)

    def test_list_routines(self):
        controller = Controller()
        ex1 = Exercise("squat", "3x5")
        ex2 = Exercise("bench press", "3x5")
        ex3 = Exercise("deadlift", "1x5")
        ex4 = Exercise("press", "3x5")
        controller.add_routine("dayA", [ex1, ex2, ex3])
        controller.add_routine("dayB", [ex1, ex4, ex3])
        with patch('sys.stdout', new=io.StringIO()) as stdout:
            cli(['--list-routine'])
            expected_output = (
                "Available routines:\n"
                "dayA: squat(3x5)\n"
                "      bench press(3x5)\n"
                "      deadlift(1x5)\n\n"
                "dayB: squat(3x5)\n"
                "      press(3x5)\n"
                "      deadlift(1x5)\n")
            self.assertEqual(expected_output.strip(), stdout.getvalue().strip())

    def test_import_export(self):
        Model('empty.db')

        controller = Controller()
        with self.assertRaises(sqlite3.DatabaseError):
            controller.import_db('test/test01.py')
        controller.import_db('empty.db')

        controller.export_db('.')
        export_path = Path().joinpath('user.db')
        self.assertTrue(export_path.exists())

        empty_db_path = PosixPath('empty.db').expanduser()
        empty_db_path.unlink()
        export_path.unlink()


if __name__ == '__main__':
    unittest.main()
