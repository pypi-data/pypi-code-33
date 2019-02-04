#!/usr/bin/env python

from setuptools import find_packages, setup

__version__ = '2.0.3'

requires = [
    'arrow>=0.13.0,<0.14.0',
    'emails>=0.5.15,<0.6.0',
    'PyMySQL>=0.9.3,<0.10.0',
    'redis>=3.1.0,<3.2.0',
    'schematics>=2.1.0,<2.2.0',
    'SQLAlchemy-Utils>=0.33.11,<0.34.0',
    'SQLAlchemy>=1.2.17,<1.3.0',
    'toml>=0.10.0,<0.11.0',
]

DESCRIPTION = """This is Danqing's shared Python library, for [the better Danqing](https://www.danqing.co).

This library provides convenient APIs for dealing with SQLAlchemy, Redis, configurations, logging, and many other things. The full documentation can be found at the [documentation site](https://dqpy.danqing.io).
"""

setup(
    name='dqpy',
    version=__version__,
    description='Danqing\'s shared Python library',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Danqing Liu',
    author_email='code@danqing.io',
    url='https://github.com/danqing/dqpy',
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        'console_scripts': ['dbadmin=dq.dbadmin:main'],
    },
    zip_safe=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
)
