#!/usr/bin/env python3
from setuptools import setup

version = '1.0.1'

setup(
    name='pro-net-algorithm',
    packages=['pronet_algorithm'],
    install_requires=[],
    version=version,
    description='A base class for long running algorithms.',
    author='ProcessGraph.Net',
    author_email='info@processgraph.net',
    url='https://github.com/processgraph-net/pro-net-algorithm',
    download_url='https://github.com/processgraph-net/pro-net-algorithm\
/archive/v' + version + '.tar.gz',
    keywords=[
        'ProcessGraph',
        'Algorithm',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    long_description="""
Pro-Net-Algorithm
------------

A base class for long running algorithms.
"""
)
