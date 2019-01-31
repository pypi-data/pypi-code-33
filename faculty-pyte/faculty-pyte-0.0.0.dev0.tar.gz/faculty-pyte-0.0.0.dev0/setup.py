#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Terminals :: Terminal Emulators/X Terminals",
]


setup(name="faculty-pyte",
      version="0.0.0.dev0",
      packages=["pyte"],
      install_requires=["wcwidth"],
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      platforms=["any"],

      author="Faculty",
      classifiers=CLASSIFIERS,
      keywords=["vt102", "vte", "terminal emulator"],
      url="https://www.asidatascience.com/")
