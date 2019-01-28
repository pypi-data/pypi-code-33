#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python library for Alphalogic Service Manager.
"""

import sys
import platform
from setuptools import setup
from api import __version__


cur = 'win32' if sys.platform == 'win32' else platform.linux_distribution()[0].lower()
ext = '.zip' if sys.platform == 'win32' else '.tar.gz'

bin_name = 'asm_api-%s-%s%s' % (cur, __version__, ext)


if __name__ == '__main__':

    with open('README.md', 'r') as fh:
        long_description = fh.read()

    setup(
        name='asm-api',
        version=__version__,
        description=__doc__.replace('\n', '').strip(),
        long_description=long_description,
        author='Alphaopen',
        author_email='mo@alphaopen.com',
        url='https://github.com/Alphaopen/asm_api',
        py_modules=['asm_api', 'asm', 'clparser'],
        include_package_data=True,
        packages=[
            'api',
        ],
        classifiers=(
            "Programming Language :: Python :: 2.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        license='MIT',
        platforms=['linux2', 'win32'],
        install_requires=[
            'requests==2.19.1',
        ],
    )