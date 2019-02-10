#!/usr/bin/env python3
from setuptools import setup

version = '1.0.2'

setup(
    name='pro-net-dynamic-task',
    packages=['pronet_dynamic_task'],
    install_requires=[
        'pronet_task',
    ],
    version=version,
    description='A task meta object to track long running dynamic\
        loaded algorithms.',
    author='ProcessGraph.Net',
    author_email='info@processgraph.net',
    url='https://github.com/processgraph-net/pro-net-dynamic-task',
    download_url='https://github.com/processgraph-net/pro-net-dynamic-task\
/archive/v' + version + '.tar.gz',
    keywords=[
        'ProcessGraph',
        'Task',
        'dynamic',
        'importlib'],
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
Pro-Net-Dynamic-Task
------------

A task meta object to track long running dynamic loaded algorithms.
"""
)
