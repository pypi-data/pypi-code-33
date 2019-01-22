# -*- coding: utf-8 -*-
import os
from abc import ABCMeta, abstractmethod
from typing import Union, List, Optional, Tuple

import attr
import pipfile
from pytesting_utils import Preconditions


@attr.s
class RunResult(object):
    statements: int = attr.ib(default=-1)
    missing: int = attr.ib(default=-1)
    coverage: float = attr.ib(default=-1.0)
    failed: int = attr.ib(default=-1)
    passed: int = attr.ib(default=-1)
    skipped: int = attr.ib(default=-1)
    warnings: int = attr.ib(default=-1)
    error: int = attr.ib(default=-1)
    time: float = attr.ib(default=-1.0)
    runner: str = attr.ib(default="")


class AbstractRunner(metaclass=ABCMeta):
    def __init__(
        self, project_name: str, path: Union[bytes, str, os.PathLike]
    ) -> None:
        Preconditions.check_argument(
            len(project_name) > 0, "Project name must not be empty!"
        )
        Preconditions.check_argument(len(path) > 0, "Path must not be empty!")
        self._project_name = project_name
        self._path = path

    @abstractmethod
    def run(self) -> Optional[Tuple[str, str]]:
        pass  # pragma: no cover

    @abstractmethod
    def get_run_result(self, log: str) -> RunResult:
        pass  # pragma: no cover

    def _extract_necessary_packages(self) -> List[str]:
        packages = []
        file_names = [
            "requirements.txt",
            "dev-requirements.txt",
            "dev_requirements.txt",
            "test-requirements.txt",
            "test_requirements.txt",
            "requirements-dev.txt",
            "requirements_dev.txt",
            "requirements-test.txt",
            "requirements_test.txt",
        ]
        for file_name in file_names:
            packages.extend(
                self._extract_packages(os.path.join(self._path, file_name))
            )
        if os.path.exists(
            os.path.join(self._path, "Pipfile")
        ) and os.path.isfile(os.path.join(self._path, "Pipfile")):
            packages.extend(self._extract_packages_from_pipfile())
        return packages

    @staticmethod
    def _extract_packages(requirements_file):
        packages = []
        if os.path.exists(requirements_file) and os.path.isfile(
            requirements_file
        ):
            with open(requirements_file) as f:
                for line in f.readlines():
                    if "requirements" in line:
                        continue
                    packages.append(line.strip())
        return packages

    def _extract_packages_from_pipfile(self) -> List[str]:
        packages = []
        p = pipfile.load(os.path.join(self._path, "Pipfile"))
        data = p.data
        if len(data["default"]) > 0:
            for k, v in data["default"].items():
                packages.append(k)
        if len(data["develop"]) > 0:
            for k, v in data["develop"].items():
                packages.append(k)
        return packages

    def __str__(self) -> str:
        return "Runner for project {} in path {} (type {})".format(
            self._project_name, self._path, type(self).__name__
        )

    def __repr__(self) -> str:
        return self.__str__()
