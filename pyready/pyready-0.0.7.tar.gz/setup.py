#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='pyready',
    version='0.0.7',
    description='Checking if services are up and running',
    author='Binh Vu',
    author_email='binhlvu@gmail.com',
    url='https://github.com/binh-vu/py-ready',
    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=["psycopg2-binary"]
)
