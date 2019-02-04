#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

VERSION = open('VERSION', 'r').read().strip()

setup(
    name='pylzmat',
    version=VERSION,
    description='lzmat bindings.',
    author='Marcos Agüero',
    author_email='wiredrat@gmail.com',
    url='https://github.com/wiredrat/pylzmat',
    long_description='''
        Bindings for lzmat library (http://www.matcode.com/lzmat.htm).
''',
    license="GNU GPLv2",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    py_modules=['pylzmat'],
    setup_requires=["cffi>1.0.0"],
    cffi_modules=["pylzmat_build.py:ffibuilder"],
    install_requires=["cffi>1.0.0"],
)
