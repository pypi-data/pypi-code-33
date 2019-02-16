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
    'redis>=3.0.0',
]

setup_requirements = [ ]

test_requirements = [
    'fakeredis>=1.0',
]

setup(
    author="G.Ted",
    author_email='gted221@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Blackboard pattern implementation",
    entry_points={
        'console_scripts': [
            'gblackboard=gblackboard.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='gblackboard',
    name='gblackboard',
    packages=find_packages(include=['gblackboard']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/GTedHa/gblackboard',
    version='0.2.0',
    zip_safe=False,
)
