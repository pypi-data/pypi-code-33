# DQSEGDB2
# Copyright (C) 2018  Duncan Macleod
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Install script for DQSEGDB2
"""

import os
import re
import sys

from setuptools import (setup, find_packages)

cmdclass = {}


def parse_version(path):
    """Extract the `__version__` string from the given file
    """
    with open(path, 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# declare dependencies
setup_requires = ['setuptools']
install_requires = ['ligo-segments', 'gwdatafind'],
tests_require = ['pytest']
if {'pytest', 'test'}.intersection(sys.argv):
    setup_requires.append('pytest_runner')

# add sphinx integration
if {'build_sphinx'}.intersection(sys.argv):
    setup_requires.extend((
        'sphinx',
        'sphinx_rtd_theme',
        'sphinx_automodapi',
        'sphinx_tabs',
        'numpydoc',
    ))
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc

# read description
with open('README.md', 'rb') as f:
    longdesc = f.read().decode().strip()

setup(
    name='dqsegdb2',
    version=parse_version(os.path.join('dqsegdb2', '__init__.py')),
    author='Duncan Macleod',
    author_email='duncan.macleod@ligo.org',
    url='https://github.com/duncanmmacleod/dqsegdb2',
    description='Simplified python interface to DQSEGDB',
    long_description=longdesc,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
