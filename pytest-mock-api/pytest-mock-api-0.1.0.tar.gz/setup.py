#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-mock-api',
    version='0.1.0',
    author='Mark Patrick Harmon',
    author_email='mpatharm@gmail.com',
    maintainer='Mark Patrick Harmon',
    maintainer_email='gaucheph@gmail.com',
    license='MIT',
    url='https://github.com/gaucheph/pytest-mock-api',
    description='A mock API server with configurable routes and responses available as a fixture.',
    long_description=read('README.rst'),
    py_modules=['pytest_mock_api'],
    python_requires='>=3.6',
    install_requires=['pytest>=4.0.0'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'mock-api = pytest_mock_api',
        ],
    },
)
