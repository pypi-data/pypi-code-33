#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='codelgb',
    version="0.0.1",
    description=(
        'code'
    ),
    long_description=open('README.rst').read(),
    author='blackmonday1',
    author_email='hhr2wd@163.com',
    maintainer='blackmonday1',
    maintainer_email='hhr2wd@163.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://www.baidu.com/',
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