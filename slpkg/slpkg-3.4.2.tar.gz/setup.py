#!/usr/bin/python
# -*- coding: utf-8 -*-

# setup.py file is part of slpkg.

# Copyright 2014-2019 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://gitlab.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import time
import shutil
from slpkg.md5sum import md5
from slpkg.__metadata__ import MetaData as _meta_

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

INSTALLATION_REQUIREMENTS = []
DOCS_REQUIREMENTS = []
TESTS_REQUIREMENTS = []
OPTIONAL_REQUIREMENTS = [
    "python2-pythondialog >= 3.3.0",
    "pygraphviz >= 1.3.1"
]

# Non-Python/non-PyPI optional dependencies:
# ascii diagram: graph-easy (available from SBo repository)


def print_logo():
    if "install" not in sys.argv:
        logo_fname = os.path.join(os.path.dirname(__file__), 'logo.txt')
        with open(logo_fname, 'rb') as f:
            logo = f.read().decode('utf-8')
            print(logo)
            time.sleep(1)


print_logo()


setup(
    name="slpkg",
    packages=["slpkg", "slpkg/sbo", "slpkg/pkg", "slpkg/slack",
              "slpkg/binary"],
    scripts=["bin/slpkg"],
    version=_meta_.__version__,
    description="Package manager for Slackware installations",
    keywords=["slackware", "slpkg", "upgrade", "install", "remove",
              "view", "slackpkg", "tool", "build"],
    author=_meta_.__author__,
    author_email=_meta_.__email__,
    url="https://dslackw.gitlab.io/slpkg/",
    package_data={"": ["LICENSE", "README.md", "CHANGELOG"]},
    data_files=[("man/man8", ["man/slpkg.8"]),
                ("/etc/bash_completion.d", ["conf/slpkg.bash-completion"]),
                ("/etc/fish/completions", ["conf/slpkg.fish"])],
    install_requires=INSTALLATION_REQUIREMENTS,
    extras_require={
        "optional": OPTIONAL_REQUIREMENTS,
        "docs": DOCS_REQUIREMENTS,
        "tests": TESTS_REQUIREMENTS,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Unix Shell",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities"],
    long_description=open("README.md").read()
    )

# Install configuration files with pip.
if "install" in sys.argv:
    conf_file = [
        "conf/slpkg.conf",
        "conf/repositories.conf",
        "conf/blacklist",
        "conf/slackware-mirrors",
        "conf/default-repositories",
        "conf/custom-repositories",
        "conf/rlworkman.deps",
        "conf/pkg_security"
    ]
    if not os.path.exists(_meta_.conf_path):
        os.makedirs(_meta_.conf_path)
    for conf in conf_file:
        filename = conf.split("/")[-1]
        if os.path.isfile(_meta_.conf_path + filename):
            old = md5(_meta_.conf_path + filename)
            new = md5(conf)
            if old != new:
                shutil.copy2(conf, _meta_.conf_path + filename + ".new")
        else:
            shutil.copy2(conf, _meta_.conf_path)
    shutil.copy2(conf_file[0],
                 _meta_.conf_path + conf_file[0].split("/")[-1] + ".orig")
