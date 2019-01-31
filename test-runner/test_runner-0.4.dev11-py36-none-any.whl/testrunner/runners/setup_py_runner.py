# -*- coding: utf-8 -*-
import os
from typing import Union, Optional, Tuple

from pytesting_utils import virtualenv

from testrunner.runners.abstract_runner import AbstractRunner, RunResult


class SetupPyRunner(AbstractRunner):
    def __init__(
        self,
        project_name: str,
        path: Union[bytes, str, os.PathLike],
        time_limit: int = 0,
    ) -> None:
        super().__init__(project_name, path)
        self._time_limit = 0

    def run(self) -> Optional[Tuple[str, str]]:
        setup_py = os.path.join(self._path, "setup.py")
        if not os.path.exists(setup_py) and not os.path.isfile(setup_py):
            return None

        with virtualenv(self._project_name) as env:
            old_dir = os.getcwd()
            os.chdir(self._path)
            packages = self._extract_necessary_packages()
            env.add_packages_for_installation(packages)
            env.add_packages_for_installation("benchexec")

            if self._time_limit > 0:
                command = "runexec --timelimit={}s -- ".format(self._time_limit)
            else:
                command = "runexec -- "
            command += "python setup.py test"
            out, err = env.run_commands([command])
            if os.path.exists(
                os.path.join(os.getcwd(), "output.log")
            ) and os.path.isfile(os.path.join(os.getcwd(), "output.log")):
                with open(os.path.join(os.getcwd(), "output.log")) as f:
                    out += "\n".join(f.readlines())

            os.chdir(old_dir)
            return out, err

    def get_run_result(self, log: str) -> RunResult:
        raise NotImplementedError("Implement me!")
