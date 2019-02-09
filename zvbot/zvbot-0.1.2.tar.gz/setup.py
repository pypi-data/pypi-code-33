#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='zvbot',
    version='0.1.2',
    description='Create a virtual server for Bot Messenger Facebook with a personal account',
    long_description='see more https://github.com/zevtyardt/zvbot/blob/master/README.md',
    author='noval wahyu ramadhan',
    author_email='xnver404@gmail.com',
    url='https://github.com/zevtyardt/zvbot',
    py_modules = ['zvbot'],
    include_package_data=True,
    install_requires=[
        'mechanize',
        'requests',
        'bs4',
    ],
    license="MIT",
    zip_safe=False,
    keywords=[
        'zvbot',
        'bot',
        'messenger'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={'console_scripts': ['zvbot = zvbot:main']},
)
