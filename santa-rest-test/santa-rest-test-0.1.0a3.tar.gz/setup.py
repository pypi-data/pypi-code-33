#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open("VERSION") as f:
    VERSION = f.read().strip()

requirements = [
        'Click>=6.0',
        "pyaml",
        "Jinja2",
        "jq",
        "aiohttp",
        ]

setup_requirements = ['pytest-runner', ]

test_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-asyncio'
]

setup(
    author="Bruno Dupuis",
    author_email='lisael@lisael.org',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Easy API testing.",
    entry_points={
        'console_scripts': [
            'santa=santa.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='santa',
    name='santa-rest-test',
    packages=find_packages(include=['santa*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lisael/santa',
    version=VERSION,
    zip_safe=False,
)

