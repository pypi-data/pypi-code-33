# -*- coding: utf-8 -*-
import os
from typing import Union, Optional, Tuple

from testrunner.runners.abstract_runner import AbstractRunner, RunResult


class ToxRunner(AbstractRunner):
    def __init__(
        self, project_name: str, path: Union[bytes, str, os.PathLike]
    ) -> None:
        super().__init__(project_name, path)  # pragma: no cover

    def run(self) -> Optional[Tuple[str, str]]:
        pass  # pragma: no cover

    def get_run_result(self, log: str) -> RunResult:
        pass  # pragma: no cover
