#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    long_description = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# Required python libraries
# requirements = []

setup(
    name="squealer",
    version="0.3.5",
    author="jackal",
    author_email="pep8@pm.me",
    description="Another sqlite wrapper",
    long_description=long_description + '\n\n' + history,
    url='https://github.com/andressl91/squealer',
    packages=find_packages(exclude=['tests*']),
    license="MIT license",
    keywords="sqlite sqlite3 development",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
)

setup(
)
