#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    'Flask==1.0.2',
    'flask_cors==3.0.6', 
    'Flask-SocketIO==3.0.2',
    'jsonmerge==1.5.2'
]

setup(
    name='appfly',
    author="Italo José G. de Oliveira",
    author_email='italo.i@live.com',
    description="This pkg encapsulate the base flask server configurations",
    install_requires=requirements,
    license="MIT license",
    long_description=open('README.md').read(),
    packages=find_packages(),
    url='https://github.com/italojs/appfly',
    version='0.2.3'
)
