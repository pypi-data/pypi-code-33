#!/usr/bin/env python3
#
# DEWI: a developer tool and framework
# Copyright (C) 2012-2018  Laszlo Attila Toth
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


import sys

if sys.hexversion < 0x03060000:
    raise RuntimeError("Required python version: 3.6 or newer (current: %s)" % sys.version)

try:
    from setuptools import setup, find_packages

except ImportError:
    from distutils.core import setup

setup(
    name="dewi",
    description="DEWI - A toolchain and framework for everyday tasks",
    long_description=\
    """
    DEWI is started as a developer tool, but contains many different dewi_commands.commands (small tools).

    It is a meta package for the DEWI packages and provides a command-line
    application for the commands in dewi_commands package.
    """,
    license="LGPLv3",
    version="2.0.0",
    author="Laszlo Attila Toth",
    author_email="python-dewi@laszloattilatoth.me",
    maintainer="Laszlo Attila Toth",
    maintainer_email="python-dewi@laszloattilatoth.me",
    keywords='tool framework development synchronization',
    url="https://github.com/LA-Toth/dewi",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Filesystems',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Utilities',
    ],
    zip_safe=True,
    use_2to3=False,
    python_requires='>=3.6',
    packages=find_packages(exclude=['pylintcheckers', '*test*']),
    entry_points={
        'console_scripts': [
            'dewi=dewi.__main__:main',
        ]
    },
    install_requires=[
        'dewi_core>=2.0.1',
        'dewi_commands>=2.0.0',
    ]
)
