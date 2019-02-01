#!/usr/bin/env python
import os.path
import codecs
import re
import sys

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = [
    'PyYAML',
    'argh',
    'pathtools',
    'aiohttp',
    'watchdog',
    'Jinja2',
    'dynaconf',
]


setup(
    name="validator-devel",
    version=find_version("validator_devel", "__init__.py"),
    description="Utility manager for handle globo modules.",
    author="Mattia Rossi",
    packages=find_packages(exclude=['tests*']),
    py_modules=['validator_entrypoint'],
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        validator-devel=validator_entrypoint:cli
    ''',
)
