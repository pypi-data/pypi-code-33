#!/usr/bin/env python3
from setuptools import setup

version = '1.0.0'

setup(
    name='pro-net-worker',
    packages=['pronet_worker'],
    install_requires=[
        'pro-net-task',
        'pro-net-dynamic-task'
    ],
    version=version,
    description='A process pool to execute tasks and dynamic tasks.',
    author='ProcessGraph.Net',
    author_email='info@processgraph.net',
    url='https://github.com/processgraph-net/pro-net-worker',
    download_url='https://github.com/processgraph-net/pro-net-worker\
/archive/v' + version + '.tar.gz',
    keywords=[
        'ProcessGraph',
        'Task',
        'Worker',
        'multiprocessing',
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
Pro-Net-Worker
------------

A process pool to execute tasks and dynamic tasks.
"""
)
