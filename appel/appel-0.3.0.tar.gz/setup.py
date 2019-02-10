#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'PyDrive>=1.3.1',
    'python-dateutil>=2.7.3',
    'PyYAML>=4.2b1',
    'requests>=2.20.0',
    'pytz>=2018.5',
    'terminaltables>=3.1.0',
    'six>=1.12.0'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Cem Gokmen",
    author_email='team@zucc.io',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Appel contains tools to process Google Spreadsheets for attendance records and store results on Canvas.",
    entry_points={
        'console_scripts': [
            'appel=appel.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='appel',
    name='appel',
    packages=find_packages(include=['appel']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/zucchini/appel',
    version='0.3.0',
    zip_safe=False,
)
