# -*- coding=utf-8 -*-

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def readlines(fname):
    return [x.strip('\n') for x in open(os.path.join(os.path.dirname(__file__), fname)).readlines()]

setup(
    name='taza',
    version='1.0.0',
    author='Daniel Domínguez',
    author_email='daniel.dominguez@imdea.org',
    description= ('A set of classes and abstractions for working with Tacyt'),
    license='MIT',
    keywords='mobile tacyt android',
    url = 'https://gitlab.software.imdea.org/android/taza',
    packages = ['taza', 'taza/tacyt', 'taza/tacyt/authorization'],
    long_description = read('README.md'),
    install_requires = readlines('requirements.txt'),
)

