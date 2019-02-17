#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

setup(
    name='pyrc522',
    packages=find_packages(),
    include_package_data=True,
    version='0.1.2',
    description='Python library for SPI RFID RC522 module',
    long_description='Raspberry Pi Python library for SPI RFID RC522 module.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
    ],
    author='Michael Fladischer',
    author_email='michael@fladi.at',
    url='https://github.com/fladi/pyrc522',
    license='MIT',
    install_requires=[
        'python-periphery',
        'RPi.GPIO',
    ],
)
