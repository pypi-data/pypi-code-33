#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Marius Mather",
    author_email='marius.mather@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A Python implementation of minimisation for clinical trials",
    install_requires=requirements,
    license="Mozilla Public License 2.0 (MPL 2.0)",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='smallerize',
    name='smallerize',
    packages=find_packages(include=['smallerize']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/warsquid/smallerize',
    version='0.4.0',
    zip_safe=False,
)
