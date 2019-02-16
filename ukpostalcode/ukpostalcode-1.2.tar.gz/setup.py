#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    

setup(
    name='ukpostalcode',
    version=1.2,
    author='Jorge Quiterio',
    author_mail='eu@jquiterio.eu',
    py_modules=['ukpostalcode'],
    description='UK Post Code Format and Validation',
    url='https://git.jquiterio.eu/jquiterio/ukpostalcode',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)