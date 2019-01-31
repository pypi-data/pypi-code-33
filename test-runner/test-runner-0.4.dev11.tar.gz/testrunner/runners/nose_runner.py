# -*- coding: utf-8 -*-
import os
import re

from typing import Union

from pytesting_utils import virtualenv

from testrunner.runners.abstract_runner import AbstractRunner, RunResult


class NoseRunner(AbstractRunner):
    def __init__(
        self,
        project_name: str,
        path: Union[bytes, str, os.PathLike],
        time_limit: int = 0,
    ) -> None:
        super().__init__(project_name, path)
        self._time_limit = time_limit

    def run(self):

        with virtualenv(self._project_name) as env:
            old_dir = os.getcwd()
            os.chdir(self._path)

            packages = self._extract_necessary_packages()
            env.add_packages_for_installation(packages)
            env.add_package_for_installation("nose")
            env.add_package_for_installation("coverage")
            env.add_package_for_installation("benchexec")

            if self._time_limit > 0:
                command = "runexec --timelimit={}s -- ".format(self._time_limit)
            else:
                command = "runexec -- "
            command += "nosetests --with-coverage --cover-erase"
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

        matches = re.search(r"Ran ([0-9]+) tests in ([0-9.]+)s", log)
        if matches:
            ran = int(matches.group(1)) if matches.group(1) else 0
            time = float(matches.group(2)) if matches.group(2) else 0.0
            passed = ran

        matches = re.search(r"SKIP=([0-9]+)", log)
        if matches:
            skipped = int(matches.group(1)) if matches.group(1) else 0
            passed -= skipped

        matches = re.search(r"DEPRECATED=([0-9]+)", log)
        if matches:
            deprecated = int(matches.group(1)) if matches.group(1) else 0
            passed -= deprecated

        matches = re.search(r"TODO=([0-9]+)", log)
        if matches:
            todo = int(matches.group(1)) if matches.group(1) else 0
            passed -= todo

        matches = re.search(r"failures=([0-9]+)", log)
        if matches:
            failed = int(matches.group(1)) if matches.group(1) else 0
            passed -= failed

        matches = re.search(r"errors=([0-9]+)", log)
        if matches:
            error = int(matches.group(1)) if matches.group(1) else 0
            passed -= error

        matches = re.search(
            r"TOTAL\s+" r"([0-9]+)\s+" r"([0-9]+)\s +" r"([0-9]+%)+", log
        )
        if matches:
            statements = int(matches.group(1)) if matches.group(1) else 0
            missing = int(matches.group(2)) if matches.group(1) else 0
            coverage = float(matches.group(3)[:-1]) if matches.group(3) else 0.0

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
            runner="nose",
        )
        return result
