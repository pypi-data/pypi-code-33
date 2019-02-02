#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='dfilter',
    version=0.2,
    description=(
        'use this filter to analys pandas quicker and smarter'
    ),
    long_description=open('README.rst').read(),
    author='yinghe sun',
    author_email='378704735@qq.com',
    maintainer='Lasso',
    maintainer_email='yinghelasso@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/YingheSun/dfilter',
    install_requires=[
        'numpy',
        'scipy',
        'prettytable'
    ],
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
)
