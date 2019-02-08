# /usr/bin/env python

# This file is part of pyspring.

# Types-and-Variables is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pyspring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pyspring.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pyspring",
    version="0.0.1",
    description="Functions that function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="harens",
    license="GPLv3",
    packages=find_packages(exclude=("tests",)),
    author_email="harensdeveloper@gmail.com",
    url="https://harens.github.io",
    download_url="https://github.com/harens/pyspring/archive/master.zip",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        "Source": "https://github.com/harens/pyspring",
        "Tracker": "https://github.com/harens/pyspring/issues",
    },
    keywords="Functions, Spring, Test",
)