# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test
import textwrap


class IntegrationTestCommand(test, object):
    """A custom command to run integration tests"""
    description = 'Test integration with a GraceDB server'

    def finalize_options(self):
        """
        Default to integration tests if test_suite and test_module are not
        set, rather than the full test suite.
        """
        if self.test_suite is None and self.test_module is None:
            self.test_suite = \
                'ligo.gracedb.test.integration.IntegrationTestSuite'
        super(IntegrationTestCommand, self).finalize_options()


def parse_version(path):
    """Extract the `__version__` string from the given file"""
    with open(path, 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Required packages for tests
tests_require = [
    'pytest>=3.1',
]
if sys.version_info.major < 3:
    tests_require.append('mock')


# Call setup()
setup(
    name="ligo-gracedb",
    version=parse_version(os.path.join('ligo', 'gracedb', 'version.py')),
    maintainer="Tanner Prestegard, Alexander Pace",
    maintainer_email="tanner.prestegard@ligo.org, alexander.pace@ligo.org",
    description="A Python package for accessing the GraceDB API",
    long_description=textwrap.dedent("""\
        The gravitational wave candidate event database (GraceDB) is a system
        to organize candidate events from gravitational wave searches and to
        provide an environment to record information about follow-ups. This
        package provides client tool to interact with the GraceDB API.
    """),
    url="https://git.ligo.org/lscsoft/gracedb-client",
    license='GPLv2+',
    namespace_packages=['ligo'],
    packages=find_packages(),
    install_requires=['future', 'six'],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=tests_require,
    package_data={
        'ligo.gracedb.test': [
            'integration/data/*',
            'integration/test.sh',
            'integration/README',
        ],
    },
    entry_points={
        'console_scripts': [
            'gracedb=ligo.gracedb.cli:main',
        ],
    },
    cmdclass={'integration_test': IntegrationTestCommand},
)
