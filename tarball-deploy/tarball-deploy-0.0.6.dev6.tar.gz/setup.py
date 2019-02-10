#!/usr/bin/env python3

from setuptools import setup

setup(
    setup_requires=["pbr>=5.1.1,<6", "pytest-runner>=4.2,<5"],
    tests_require=["pytest>=4.2.0,<5"],
    pbr=True,
)
