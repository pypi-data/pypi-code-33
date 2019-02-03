# -*- coding: utf-8 -*-
import os
from enum import Enum, auto
from typing import Union, Tuple

from plumbum import local
from pytesting_utils import IllegalStateException, Preconditions

from testrunner.runners.abstract_runner import AbstractRunner, RunResult
from testrunner.runners.nose2_runner import Nose2Runner
from testrunner.runners.nose_runner import NoseRunner
from testrunner.runners.pytest_runner import PyTestRunner
from testrunner.runners.setup_py_runner import SetupPyRunner


class RunnerType(Enum):
    """Various types of known runners"""

    AUTO_DETECT = auto()
    """Use the auto-detection for the correct runner.
    ATTENTION: This is not yet implemented!"""

    PYTEST = auto()
    """Use the PyTest runner."""

    SETUP_PY = auto()
    """Use setup.py test as runner."""

    NOSE = auto()
    """Use the nose runner."""

    NOSE2 = auto()
    """Use the nose2 runner."""

    _UNKNOWN = auto()


class Runner(object):
    """
    The runner
    """

    def __init__(
        self,
        project_name: str,
        repo_path: Union[bytes, str, os.PathLike],
        runner: RunnerType = RunnerType.AUTO_DETECT,
        time_limit: int = 0,
        junit_xml_file: Union[bytes, str, os.PathLike] = None,
        venv_path: Union[bytes, str, os.PathLike] = None,
    ) -> None:
        """
        Creates a new runner for tests.

        :param project_name: The name of the project
        :param repo_path: Path to the project's source code
        :param runner: The RunnerType that should be used
        :param time_limit: An optional time limit for the execution (in seconds)
        :param junit_xml_file: Create an JUnit-like XML file from the runs (
        only for PyTest)
        :param venv_path: Path where the temporary venv will be created
         (only for PyTest)
        """
        Preconditions.check_argument(
            time_limit >= 0, "A specified time limit has to be at least 0!"
        )
        self._project_name = project_name
        self._repo_path = repo_path
        self._time_limit = time_limit
        self._junit_xml_file = junit_xml_file
        self._venv_path = venv_path
        self._grep = local["grep"]

        if runner != RunnerType.AUTO_DETECT:
            self._runner_type = runner
        else:
            self._runner_type = self._detect_runner_type()
        self._runner = self._instantiate_runner()

    def _detect_runner_type(self) -> RunnerType:
        if self._is_pytest():
            return RunnerType.PYTEST
        elif self._is_nose2():
            return RunnerType.NOSE2
        elif self._is_nose():
            return RunnerType.NOSE
        elif self._is_setup_py():
            return RunnerType.SETUP_PY
        return RunnerType._UNKNOWN  # pragma: no cover

    def _instantiate_runner(self) -> AbstractRunner:
        if self._runner_type == RunnerType.PYTEST:
            runner = PyTestRunner(
                self._project_name,
                self._repo_path,
                self._time_limit,
                self._junit_xml_file,
                self._venv_path,
            )
        elif self._runner_type == RunnerType.SETUP_PY:
            runner = SetupPyRunner(
                self._project_name, self._repo_path, self._time_limit
            )
        elif self._runner_type == RunnerType.NOSE:
            runner = NoseRunner(
                self._project_name, self._repo_path, self._time_limit
            )
        elif self._runner_type == RunnerType.NOSE2:
            runner = Nose2Runner(
                self._project_name, self._repo_path, self._time_limit
            )
        else:
            raise IllegalStateException("Could not find a matching runner!")
        return runner

    def _is_pytest(self) -> bool:
        if os.path.exists(
            os.path.join(self._repo_path, "setup.py")
        ) and os.path.isfile(os.path.join(self._repo_path, "setup.py")):
            _, r, _ = self._grep[
                "test_suite=pytest", os.path.join(self._repo_path, "setup.py")
            ].run(retcode=None)
            if len(r) > 0:
                return True

            _, r, _ = self._grep[
                "test_suite=py.test", os.path.join(self._repo_path, "setup.py")
            ].run(retcode=None)
            if len(r) > 0:
                return True

        if os.path.exists(
            os.path.join(self._repo_path, "pytest.ini")
        ) and os.path.isfile(os.path.join(self._repo_path, "pytest.ini")):
            return True

        _, r, _ = self._grep["-R", "import pytest", self._repo_path].run(
            retcode=None
        )
        if len(r) > 0:
            return True

        _, r, _ = self._grep["-R", "from pytest import", self._repo_path].run(
            retcode=None
        )
        if len(r) > 0:
            return True

        _, r, _ = self._grep["-R", "pytest", self._repo_path].run(retcode=None)
        if len(r) > 0:
            return True

        return False

    def _is_nose2(self) -> bool:
        if os.path.exists(
            os.path.join(self._repo_path, "setup.py")
        ) and os.path.isfile(os.path.join(self._repo_path, "setup.py")):
            _, r, _ = self._grep[
                "nose2", os.path.join(self._repo_path, "setup.py")
            ].run(retcode=None)
            if len(r) > 0:
                return True
        return False

    def _is_nose(self) -> bool:
        if os.path.exists(
            os.path.join(self._repo_path, "setup.py")
        ) and os.path.isfile(os.path.join(self._repo_path, "setup.py")):
            _, r, _ = self._grep[
                "nose", os.path.join(self._repo_path, "setup.py")
            ].run(retcode=None)
            if len(r) > 0:
                return True
        return False

    def _is_setup_py(self) -> bool:
        if os.path.exists(
            os.path.join(self._repo_path, "setup.py")
        ) and os.path.isfile(os.path.join(self._repo_path, "setup.py")):
            _, r, _ = self._grep[
                "test_suite=", os.path.join(self._repo_path, "setup.py")
            ].run(retcode=None)
            if len(r) > 0:
                return True

        return False

    def run(self) -> Tuple[str, str]:
        """
        Run the test runner for the project

        :return: A tuple (stdout, stderr) with the outputs of the run process
        """
        return self._runner.run()

    def get_run_result(self, result: str) -> RunResult:
        """
        Parses the run results from a result string created by the run method.

        :param result: The output of the run method
        :return: A run-result object containing the extracted information
        """
        return self._runner.get_run_result(result)
