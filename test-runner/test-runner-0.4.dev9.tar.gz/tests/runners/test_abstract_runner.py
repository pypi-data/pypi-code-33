# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from pytesting_utils import IllegalArgumentException

from testrunner.runners.abstract_runner import AbstractRunner


class AbstractRunnerTest(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        files = {
            "requirements.txt": "foo",
            "dev-requirements.txt": "bar",
            "test-requirements.txt": "baz",
            "requirements-test.txt": "-r requirements.txt",
        }
        for k, v in files.items():
            with open(os.path.join(self._tmp_dir, k), "w") as f:
                f.write(v)

    def tearDown(self):
        shutil.rmtree(self._tmp_dir)

    def test_cannot_instantiate(self):
        """Showing we normally cannot instantiate an abstract class"""
        with self.assertRaises(TypeError):
            AbstractRunner("foo", "bar")

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_empty_project_name(self):
        with self.assertRaises(IllegalArgumentException) as context:
            AbstractRunner("", "bar")
        self.assertTrue(isinstance(context.exception, IllegalArgumentException))
        self.assertTrue(
            "Project name must not be empty!" in str(context.exception)
        )

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_empty_path(self):
        with self.assertRaises(IllegalArgumentException) as context:
            AbstractRunner("foo", "")
        self.assertTrue(isinstance(context.exception, IllegalArgumentException))
        self.assertTrue("Path must not be empty!" in str(context.exception))

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_extract_necessary_packages(self):
        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner._extract_necessary_packages()
        self.assertTrue("foo" in result)
        self.assertTrue("bar" in result)
        self.assertTrue("baz" in result)

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_string_representation(self):
        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner.__str__()
        expected = (
            "Runner for project foo in path {} (type "
            "AbstractRunner)".format(self._tmp_dir)
        )
        self.assertEqual(expected, result)

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_extract_packages_from_empty_pipfile(self):
        with open(os.path.join(self._tmp_dir, "Pipfile"), "w") as f:
            f.write(
                """
[scripts]
tests = "bash ./run-tests.sh"
            """
            )

        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner._extract_packages_from_pipfile()
        self.assertListEqual([], result)

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_extract_packages_from_pipfile(self):
        with open(os.path.join(self._tmp_dir, "Pipfile"), "w") as f:
            f.write(
                """[packages]
mock = "*"
sphinx = "<=1.5.5"
            """
            )

        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner._extract_packages_from_pipfile()
        self.assertListEqual(["mock", "sphinx"], result)

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_extract_dev_packages_from_pipfile(self):
        with open(os.path.join(self._tmp_dir, "Pipfile"), "w") as f:
            f.write(
                """[dev-packages]
"flake8" = ">=3.3.0,<4"
pipenv = {path = ".", editable = true}
            """
            )

        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner._extract_packages_from_pipfile()
        self.assertListEqual(["flake8", "pipenv"], result)

    @patch.multiple(AbstractRunner, __abstractmethods__=set())
    def test_extract_all_packages_from_pipfile(self):
        with open(os.path.join(self._tmp_dir, "Pipfile"), "w") as f:
            f.write(
                """[dev-packages]
"flake8" = ">=3.3.0,<4"
pipenv = {path = ".", editable = true}

[packages]
mock = "*"
sphinx = "<=1.5.5"
            """
            )

        runner = AbstractRunner("foo", self._tmp_dir)
        result = runner._extract_packages_from_pipfile()
        self.assertListEqual(["mock", "sphinx", "flake8", "pipenv"], result)


if __name__ == "__main__":
    unittest.main()
