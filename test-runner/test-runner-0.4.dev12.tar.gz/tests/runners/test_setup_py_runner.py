# -*- coding: utf-8 -*-
import shutil
import tempfile
import unittest
from git import Repo

from testrunner.runners.setup_py_runner import SetupPyRunner


class SetupPyRunnerTest(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        url = "https://github.com/audreyr/standardjson"
        self._repo = Repo.clone_from(url, self._tmp_dir)
        self._runner = SetupPyRunner("standardjson", self._tmp_dir)

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_run(self):
        out, err = self._runner.run()
        # self.assertFalse("error" in err.lower())
        self.assertTrue("passed" in out.lower())

    def test_run_no_setup_py(self):
        runner = SetupPyRunner("test", "test")
        result = runner.run()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
