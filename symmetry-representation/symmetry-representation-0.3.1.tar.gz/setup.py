#!/usr/bin/env python
# -*- coding: utf-8 -*-

# © 2017-2018, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>

import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
if sys.version_info < (3, 5):
    raise 'must use Python version 3.5 or higher'

README = """A tool to describe symmetry operations and their representation."""

with open('./symmetry_representation/__init__.py', 'r') as f:
    MATCH_EXPR = "__version__[^'\"]+(['\"])([^'\"]+)"
    VERSION = re.search(MATCH_EXPR, f.read()).group(2).strip()

setup(
    name='symmetry-representation',
    version=VERSION,
    url='http://z2pack.ethz.ch/symmetry-representation',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    license='Apache 2.0',
    description='Provides an interface to describe symmetry representations.',
    install_requires=[
        'numpy', 'sympy', 'fsc.export', 'fsc.hdf5-io>=0.5', 'h5py', 'pymatgen',
        'click>=7.0'
    ],
    extras_require={
        'dev': [
            'pytest', 'pytest-cov', 'yapf==0.24', 'pre-commit==1.11.1',
            'sphinx', 'sphinx-rtd-theme', 'sphinx-click', 'ipython>=6.2',
            'prospector==1.1.6.*', 'pylint==2.1.*'
        ]
    },
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English', 'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 4 - Beta'
    ],
    packages=[
        'symmetry_representation', 'symmetry_representation._get_repr_matrix'
    ],
    entry_points='''
        [console_scripts]
        symmetry-repr=symmetry_representation._cli:cli
    ''',
)
