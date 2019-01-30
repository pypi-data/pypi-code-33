#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join
from setuptools import setup

import djangocms_maps as package

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Communications',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]


def read(*pathcomponents):
    """Read the contents of a file located relative to setup.py"""
    with open(join(abspath(dirname(__file__)), *pathcomponents)) as thefile:
        return thefile.read()


setup(
    name='djangocms-maps',
    version=package.__version__,
    description=package.__doc__.strip(),
    author=package.__author__,
    author_email=package.__email__,
    url=package.__url__,
    packages=[
        'djangocms_maps',
        'djangocms_maps.migrations',
        'djangocms_maps.templatetags',
    ],
    license=package.__license__,
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description='\n'.join([read('README.rst'), read('CHANGELOG.rst')]),
    include_package_data=True,
    zip_safe=False
)
