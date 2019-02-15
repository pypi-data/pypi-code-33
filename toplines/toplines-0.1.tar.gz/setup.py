#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name = 'toplines',
    version = '0.1',
    description = 'Get top lines from a large file',
    author = 'haierol',
    author_email = 'haierol@qq.com',
    maintainer = '51pricing',
    maintainer_email = '51pricing@haianfund.com',
    license = 'MIT License',
    packages = find_packages(),
    platforms = ["all"],
    url = 'https://github.com/51pricing/toplines',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires = [
        'click',
        ],
    entry_points = {
        'console_scripts': [
        'toplines = toplines.main:cmd'
        ]
        },
)