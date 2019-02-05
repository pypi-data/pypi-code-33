#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the UniqueID service."""
from os import path
try:  # pip version 9
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt', session='hack')

setup(
    name='pacifica-uniqueid',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica UniqueID',
    url='https://pypi.python.org/pypi/pacifica-uniqueid/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='david.brown@pnnl.gov',
    packages=find_packages(),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-uniqueid=pacifica.uniqueid.__main__:main',
            'pacifica-uniqueid-cmd=pacifica.uniqueid.__main__:cmd'
        ]
    },
    install_requires=[str(ir.req) for ir in INSTALL_REQS]
)
