# -*- coding: utf-8 -*-
"""
Test runner is a library for running unit tests on Python code.

It offers the opinion to automatically detect the correct run settings for
the tests and gives information about the test results and coverage information.

Test-Runner is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Test-Runner is distributed in the hope that it will be useful
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Test-Runner.  If not, see <https://www.gnu.org/licenses/>.
"""
__all__ = ["Runner", "RunnerType", "RunResult"]
from testrunner.runner import Runner, RunnerType  # noqa: F401
from testrunner.runners.abstract_runner import RunResult  # noqa: F401

__version__ = "0.4.dev8"
__name__ = "test-runner"
__author__ = "Stephan Lukasczyk"
