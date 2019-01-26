#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# System modules
import os
import sys
import re
import runpy
from setuptools import setup, find_packages


def read_file(filename):
    with open(filename, errors="ignore") as f:
        return f.read()


package = find_packages(exclude=["tests"])[0]

# run setup
setup(
    name=re.sub("_", "-", package),
    description="Python class utilities",
    author="Yann Büchau",
    author_email="nobodyinperson@gmx.de",
    keywords="",
    license="GPLv3",
    version=runpy.run_path(os.path.join(package, "version.py")).get(
        "__version__", "0.0.0"
    ),
    url="https://gitlab.com/nobodyinperson/python3-class-tools",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    install_requires=[],
    tests_require=[],
    extras_require={},
    test_suite="tests",
    packages=[package],
)
