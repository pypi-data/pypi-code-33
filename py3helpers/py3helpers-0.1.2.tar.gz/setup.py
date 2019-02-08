#!/usr/bin/env python3
"""Create setup script for pip installation of python_utils"""
########################################################################
# File: setup.py
#  executable: setup.py
#
# Author: Andrew Bailey
# History: 12/09/17 Created
########################################################################

import sys
from timeit import default_timer as timer
from setuptools import setup, find_packages


def main():
    """Main docstring"""
    start = timer()
    setup(
        name="py3helpers",
        version='0.1.2',
        description='Python utility functions',
        url='https://github.com/adbailey4/python_utils',
        author='Andrew Bailey',
        license='MIT',
        author_email='andbaile@ucsc.com',
        setup_requires=["pytest-runner>=2.0"],
        tests_require=["pytest>=4.0.0"],
        packages=find_packages(),
        install_requires=['mappy>=2.14',
                          'biopython>=1.68',
                          'pysam>=0.15',
                          'numpy>=1.14.2',
                          'pandas>=0.23.4',
                          'scikit-learn>=0.19.0',
                          'matplotlib>=2.0.2',
                          'pytest-runner>=2.0'],
        zip_safe=True
    )

    stop = timer()
    print("Running Time = {} seconds".format(stop-start), file=sys.stderr)


if __name__ == "__main__":
    main()
    raise SystemExit
