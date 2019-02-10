#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='pic2x',
    version='0.14',
    description=(
        'Transform your picture to anything.'
    ),
    long_description=open('README.rst').read(),
    author='ZillyRex',
    author_email='zillyrain@gmail.com',
    maintainer='ZillyRex',
    maintainer_email='zillyrain@gmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/ZillyRex/pic2x',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)
