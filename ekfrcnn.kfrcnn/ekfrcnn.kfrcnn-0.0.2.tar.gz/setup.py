#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = open('README.md').read().split('\n')

setup(
    name='ekfrcnn.kfrcnn',
    author="Italo José G. de Oliveira",
    author_email='italo.i@live.com',
    description="This package provide a simple interface to use the Faster RCNN architecture",
    install_requires=requirements,
    license="MIT license",
    long_description=open('README.md').read(),
    packages=find_packages(),
    version='0.0.2'
)
