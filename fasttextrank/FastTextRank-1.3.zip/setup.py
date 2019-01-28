#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup (
    name='FastTextRank',
    version=1.3,
    description=(
        'Extract abstracts and keywords from Chinese text'
    ),
    long_description=open('README.rst').read(),
    author='Edward',
    author_email='artistscript@outlook.com',
    maintainer='Edward',
    maintainer_email='artistscript@outlook.com',
    license='BSD License',
    packages=['FastTextRank'],
    platforms=["all"],
    url='https://github.com/ArtistScript/FastTextRank',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'Numpy>=1.14.5',
        'gensim>=3.5.0'
    ]
)