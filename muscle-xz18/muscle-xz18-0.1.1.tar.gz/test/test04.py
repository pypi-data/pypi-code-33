import unittest
from pathlib import Path

from muscle.view.cli import cli


class TestCLI(unittest.TestCase):

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

    def test_arg_parse01(self):
        with self.assertRaises(SystemExit) as err:
            cli(['--help'])
        self.assertEqual(0, err.exception.code)

    def test_arg_parse02(self):
        with self.assertRaises(SystemExit) as err:
            cli(['--record', 'invalid arg'])
        self.assertEqual(2, err.exception.code)

    def test_arg_parse03(self):
        with self.assertRaises(SystemExit) as err:
            cli(['--record', '--gui'])
        self.assertEqual(2, err.exception.code)

    def test_arg_parse04(self):
        with self.assertRaises(SystemExit) as err:
            cli(['--delete-routine', 'routine_name', 'invalid arg'])
        self.assertEqual(2, err.exception.code)


if __name__ == '__main__':
    unittest.main()
