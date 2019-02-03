# -*- coding: utf-8 -*-
import os
import re
from typing import Union, Optional, Tuple

from pytesting_utils import virtualenv
from setuptools import find_packages

from testrunner.runners.abstract_runner import AbstractRunner, RunResult


class PyTestRunner(AbstractRunner):
    def __init__(
        self,
        project_name: str,
        path: Union[bytes, str, os.PathLike],
        time_limit: int = 0,
        junit_xml_file: Union[bytes, str, os.PathLike] = None,
        venv_path: Union[bytes, str, os.PathLike] = None,
    ) -> None:
        super().__init__(project_name, path)
        self._time_limit = time_limit
        self._junit_xml_file = junit_xml_file
        self._venv_path = venv_path

    def run(self) -> Optional[Tuple[str, str]]:
        # TODO make sure nothing goes wrong here

        with virtualenv(self._project_name, self._venv_path) as env:
            old_dir = os.getcwd()
            os.chdir(self._path)

            if "-" in self._project_name and os.path.exists(
                os.path.join(os.getcwd(), self._project_name.replace("-", ""))
            ):
                project_name = self._project_name.replace("-", "")
            elif "_" in self._project_name and os.path.exists(
                os.path.join(os.getcwd(), self._project_name.replace("_", ""))
            ):
                project_name = self._project_name.replace("_", "")
            elif "-" in self._project_name and os.path.exists(
                os.path.join(os.getcwd(), self._project_name.replace("-", "_"))
            ):
                project_name = self._project_name.replace("-", "_")
            elif os.path.exists(os.path.join(os.getcwd(), self._project_name)):
                project_name = self._project_name
            else:
                directories = find_packages(".", exclude=["test", "tests"])
                if len(directories) == 0 and os.path.exists(
                    os.path.join(os.getcwd(), "src")
                ):
                    directories = find_packages(
                        "src", exclude=["test", "tests"]
                    )
                project_name = directories[0] if len(directories) > 1 else "."

            packages = self._extract_necessary_packages()
            env.add_packages_for_installation(packages)
            env.add_package_for_installation("pytest")
            env.add_package_for_installation("pytest-cov")
            env.add_package_for_installation("benchexec")

            if self._time_limit > 0:
                command = "runexec --timelimit={}s -- ".format(self._time_limit)
            else:
                command = "runexec -- "
            command += "pytest --cov={} --cov-report=term-missing".format(
                project_name
            )
            if self._junit_xml_file is not None:
                command += " --junitxml={}".format(self._junit_xml_file)

            out, err = env.run_commands([command])
            if os.path.exists(
                os.path.join(os.getcwd(), "output.log")
            ) and os.path.isfile(os.path.join(os.getcwd(), "output.log")):
                with open(os.path.join(os.getcwd(), "output.log")) as f:
                    out += "\n".join(f.readlines())
            os.chdir(old_dir)
            return out, err

    def get_run_result(self, log: str) -> RunResult:
        statements = -1
        missing = -1
        coverage = -1.0
        failed = -1
        passed = -1
        skipped = -1
        warnings = -1
        error = -1
        time = -1.0

        matches = re.search(
            r"[=]+ (([0-9]+) failed, )?"
            r"([0-9]+) passed"
            r"(, ([0-9]+) skipped)?"
            r"(, ([0-9]+) warnings)?"
            r"(, ([0-9]+) error)?"
            r" in ([0-9.]+) seconds",
            log,
        )
        if matches:
            failed = int(matches.group(2)) if matches.group(2) else 0
            passed = int(matches.group(3)) if matches.group(3) else 0
            skipped = int(matches.group(5)) if matches.group(5) else 0
            warnings = int(matches.group(7)) if matches.group(7) else 0
            error = int(matches.group(9)) if matches.group(9) else 0
            time = float(matches.group(10)) if matches.group(10) else 0.0

        matches = re.search(
            r"TOTAL\s+"
            r"([0-9]+)\s+"
            r"([0-9]+)\s+"
            r"(([0-9]+)\s+([0-9]+)\s+)?"
            r"([0-9]+%)",
            log,
        )
        if matches:
            statements = int(matches.group(1)) if matches.group(1) else 0
            missing = int(matches.group(2)) if matches.group(2) else 0
            coverage = float(matches.group(6)[:-1]) if matches.group(6) else 0.0
        else:
            matches = re.search(
                r".py\s+"
                r"([0-9]+)\s+"
                r"([0-9]+)\s+"
                r"(([0-9]+)\s+([0-9]+)\s+)?"
                r"([0-9]+%)",
                log,
            )
            if matches:
                statements = int(matches.group(1)) if matches.group(1) else 0
                missing = int(matches.group(2)) if matches.group(2) else 0
                coverage = (
                    float(matches.group(6)[:-1]) if matches.group(6) else 0.0
                )

        result = RunResult(
            statements=statements,
            missing=missing,
            coverage=coverage,
            failed=failed,
            passed=passed,
            skipped=skipped,
            warnings=warnings,
            error=error,
            time=time,
            runner="pytest",
        )
        return result
