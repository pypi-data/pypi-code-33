#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    README = readme_file.read()

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read()

REQUIREMENTS = ['numpy>=1.9.0', 'scipy>=1.0.0', 'joblib>=0.9.2']

SETUP_REQUIREMENTS = ['pytest-runner', ]

TEST_REQUIREMENTS = ['pytest', ]

setup(
    author="Dan Vatterott",
    author_email='dvatterott@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description="Identify changes in model outputs at prediction time.",
    install_requires=REQUIREMENTS,
    license="MIT license",
    long_description=README + '\n\n' + HISTORY,
    include_package_data=True,
    keywords='predeval',
    name='predeval',
    packages=find_packages(include=['predeval']),
    setup_requires=SETUP_REQUIREMENTS,
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
    url='https://github.com/dvatterott/predeval',
    version='0.0.6',
    zip_safe=False,
)
