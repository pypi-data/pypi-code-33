#!/usr/bin/env python3
from setuptools import setup

version = '1.0'

setup(
    name='pro-net-registry',
    packages=['pronet_registry'],
    install_requires=[
        'pro-net-worker',
        'pro-net-task',
        'pro-net-dynamic-task',
    ],
    version=version,
    description='A registry for executing of long running algorithms.',
    author='ProcessGraph.Net',
    author_email='info@processgraph.net',
    url='https://github.com/processgraph-net/pro-net-registry',
    download_url='https://github.com/processgraph-net/pro-net-registry\
/archive/v' + version + '.tar.gz',
    keywords=['Process', 'Graph', 'Registry', 'mulitprocessing'],
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
Pro-Net-Registry
------------

A registry for executing of long running algorithms.
"""
)
