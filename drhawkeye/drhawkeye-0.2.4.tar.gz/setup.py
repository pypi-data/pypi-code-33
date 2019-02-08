#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, Extension, find_packages
import numpy
import os
import sys

setup(
    author="Micah Sandusky",
    author_email='micah.sandusky@ars.usda.gov',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Checking health of programs with consistent directory tree and many outputs",
    license="CC0 1.0",
    # long_description=readme + '\n\n' + history,
    include_package_data=True,
    package_data={'drhawkeye':['./CoreConfig.ini',
				  './recipes.ini']},
    keywords='drhawkeye',
    name='drhawkeye',
    packages=['drhawkeye'],
    test_suite='tests',
    # tests_require=test_requirements,
    url='https://github.com/usdaarsnwrc/drhawkeye',
    version='0.2.4',
    zip_safe=False,
    scripts=[],
)
