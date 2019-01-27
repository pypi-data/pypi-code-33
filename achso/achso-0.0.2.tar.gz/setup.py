#!/usr/bin/env python

import os
from setuptools import setup

setup(
    name='achso',
    version='0.0.2',
    author='Yuto Kisuge',
    author_email='mail@yo.eki.do',
    description='AtCoder Helper Suite',
    license='MIT',
    keywords='AtCoder',
    url='https://github.com/kissge/achso',
    packages=['achso', 'achso/commands'],
    install_requires=['cement<3', 'requests', 'lxml', 'cssselect'],
    long_description='Command Line Utilities for AtCoder',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'achso=achso:main',
        ],
    },
)
