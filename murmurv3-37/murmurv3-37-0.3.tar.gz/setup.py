#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Murmur Hash Library
===================

Murmur Hash Library is a simple c level implementation developed for
high speed hashing of in memory strings, on disk files, and the contents
of zip files.

As the name implies the hashes are generated via an implementation of
`MurmurHash 2.0`_.

A few quick NOTES and WARNINGS:

The implementation of MurMur that is used in this code makes the
following assumptions about your machine:

	1. A 4-byte value can be read from any address without crashing
	2. sizeof(int) == 4

It will also not produce the same results on little-endian and big-endian
machines.

I believe it would be easily possible to get around these limitations.

.. _MurmurHash 2.0: http://murmurhash.googlepages.com/
"""
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

setup(
    name='murmurv3-37',
    version='0.3',
    license='MIT',
    author='Jorick Caberio, Bryan McLemore',
    description='MurmurV3 for Python 3.7',
	url = 'https://github.com/jcaberio/MurmurV3',
	download_url = 'https://github.com/jcaberio/MurmurV3/tarball/0.5',
    zip_safe=False, # I'm not sure if it is egg safe so I'm erring on the side of caution.
    long_description=__doc__,
	ext_modules = [
		Extension('murmur',
		[	"murmur/murmur.cpp",
			"murmur/unzip.c",
			"murmur/ioapi.c",
		],
		depends=[
			"murmur/include/murmurcrypt.h",
			"murmur/include/ioapi.h",
			"murmur/include/unzip.h",
		],
		include_dirs=['murmur/include'],
		libraries=['z'],
		language='c++')
	],
    platforms='any',
    classifiers=[
	    'Programming Language :: Python',
	    'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: C++',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
	packages=[]
)
