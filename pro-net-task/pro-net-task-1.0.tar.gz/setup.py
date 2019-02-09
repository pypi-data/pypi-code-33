#!/usr/bin/env python3
from setuptools import setup

version = '1.0'

setup(
    name='pro-net-task',
    packages=['pronet_task'],
    install_requires=[],
    version=version,
    description='A task meta object to track long running algorithms.',
    author='ProcessGraph.Net',
    author_email='info@processgraph.net',
    url='https://github.com/processgraph-net/pro-net-task',
    download_url='https://github.com/processgraph-net/pro-net-task\
/archive/v' + version + '.tar.gz',
    keywords=['Process', 'Graph', 'ProcessGraph', 'Task'],
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
Pro-Net-Task
------------

A task meta object to track long running algorithms.
"""
)
