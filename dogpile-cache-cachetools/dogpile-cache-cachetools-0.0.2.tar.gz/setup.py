#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

init = os.path.join(os.path.dirname(__file__), 'dogpile_cache_cachetools', '__init__.py')
with open(init) as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    desc = f.read()

setup(
    name='dogpile-cache-cachetools',
    version=version,
    description='cachetool backends of dogpile.cache',
    long_description=desc,
    long_description_content_type='text/markdown',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=[
        'dogpile.cache>=0.7.1',
        'cachetools>=3.0.0',
    ],
    license='Apache Software License 2.0',
    include_package_data=True,
    keywords='dogpile.cache cachetools',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/manthey',
    zip_safe=False,
)
