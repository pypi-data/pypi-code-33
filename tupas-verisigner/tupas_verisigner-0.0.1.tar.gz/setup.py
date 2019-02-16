#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import tupas_verisigner

setup(
    name='tupas_verisigner',
    version=tupas_verisigner.__version__,
    description="TUPAS URL verification and signing",
    long_description=open('README.md').read(),
    author='Adarsh Krishnan',
    author_email='adarshk7@gmail.com',
    url='http://github.com/adarshk7/tupas_verisigner',
    license='MIT',
    py_modules=['tupas_verisigner'],
    zip_safe=False,
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
