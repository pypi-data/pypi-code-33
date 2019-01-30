#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/10/27 14:59    @Author  : xycfree
# @Descript:

from os import path

from codecs import open

# Always prefer setuptools over distutils

try:

    from setuptools import setup

except ImportError:

    from distutils.core import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ccwt_client',
    packages=['ccwt_client'],
    version='1.0.1',
    description='ccwt server client',
    url='https://github.com/nigelliyang/ccwt_client',
    # url='https://github.com/xycfree/ccwt_client',
    author='xycfree',
    author_email='xycfree@163.com',
    license='Apache v2.0 License',

    install_requires=[
        'requests>=2.18.4',
        'requests_cache>=0.4.13',
        'pyalgotrade>=0.20',
    ],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)
