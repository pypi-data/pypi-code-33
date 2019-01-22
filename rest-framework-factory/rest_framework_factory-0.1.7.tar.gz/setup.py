#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'django', 'djangorestframework']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Steven Walker",
    author_email='walker@mfgis.com',
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
    description="A factory for createing Django Rest Framework APIs",
    entry_points={
        'console_scripts': [
            'rest_framework_factory=rest_framework_factory.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='rest_framework_factory',
    name='rest_framework_factory',
    packages=find_packages(include=['rest_framework_factory']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/MiddleFork/rest_framework_factory',
    version='0.1.7',
    zip_safe=False,
)
