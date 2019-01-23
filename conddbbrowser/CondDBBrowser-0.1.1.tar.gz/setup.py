#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CondDBBrowser',
    use_scm_version=True,
    description='LHCb Conditions Database Browser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.cern.ch/lhcb/CondDBBrowser',  # Optional
    author='CERN - LHCb Core Software',
    author_email='lhcb-core-soft@cern.ch',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    install_requires=["PySide2==5.12.0"],
    tests_require=['pytest', 'pytest-cov'],
    setup_requires=['setuptools_scm', 'pytest-runner'],
    entry_points=
    {  # Optional
        'console_scripts': [
            'CondDBBrowser=CondDBBrowser:main',
        ],
    },
    zip_safe=True,
)
