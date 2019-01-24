#!/usr/bin/env python

from setuptools import setup, find_packages


PACKAGE = 'pathaccessor'

setup(
    name=PACKAGE,
    description='Track the key path into a dicts-and-lists data structure.',
    version='0.1.2',
    author='Nathan Wilcox',
    author_email='nejucomo+dev@gmail.com',
    license='GPLv3',
    url='https://github.com/nejucomo/{}'.format(PACKAGE),
    packages=find_packages(),
)
