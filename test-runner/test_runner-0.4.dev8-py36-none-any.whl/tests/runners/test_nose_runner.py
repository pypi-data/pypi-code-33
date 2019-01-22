# -*- coding: utf-8 -*-
import shutil
import tempfile
import unittest

from git import Repo

from testrunner.runners.nose_runner import NoseRunner


class NoseRunnerTest(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_integration_zula(self):
        url = "https://github.com/efe/zula"
        Repo.clone_from(url, self._tmp_dir)
        runner = NoseRunner("zula", self._tmp_dir)
        out, err = runner.run()
        result = runner.get_run_result(out)
        self.assertGreater(result.statements, 0)
        self.assertGreaterEqual(result.missing, 0)
        self.assertGreater(result.coverage, 0)

    def test_integration_ratelimitqueue(self):
        url = "https://github.com/JohnPaton/ratelimitqueue"
        Repo.clone_from(url, self._tmp_dir)
        runner = NoseRunner("ratelimitqueue", self._tmp_dir)
        out, err = runner.run()
        result = runner.get_run_result(out)
        self.assertGreater(result.statements, 0)
        self.assertGreaterEqual(result.missing, 0)
        self.assertGreater(result.coverage, 0)

    def test_integration_extra_context_py(self):
        url = "https://github.com/WanzenBug/extra-context-py"
        Repo.clone_from(url, self._tmp_dir)
        runner = NoseRunner("extra-context-py", self._tmp_dir)
        out, err = runner.run()
        result = runner.get_run_result(out)
        self.assertGreater(result.statements, 0)
        self.assertGreater(result.missing, 0)
        self.assertGreater(result.coverage, 0)

    def test_no_match(self):
        runner = NoseRunner("test", "test")
        result = runner.get_run_result("test")
        self.assertEqual(-1, result.time)
        self.assertEqual(-1, result.coverage)


if __name__ == "__main__":
    unittest.main()
