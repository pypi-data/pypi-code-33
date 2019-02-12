# -*- coding: utf-8 -*-
# Copyright 2016 João Felipe Santos, jfsantos@emt.inrs.ca
#
# This file is part of the maracas library, and is licensed under the
# MIT license.
from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name = "maracas",
    version = "0.0.1",
    packages = find_packages(),

    description = "Tools for generating noisy and reverberant audio files",
    long_description = long_description,
    long_description_content_type = "text/markdown",

    install_requires = [
        'numpy',
        'scipy',
        'numba',
        'tqdm'
    ],

    tests_require = [
        'pytest'
    ],

    setup_requires = [
        'pytest-runner'
    ],

    entry_points = {
#        'console_scripts': [
#            'maracas = maracas.maracas:main',
#        ]
    }
)

