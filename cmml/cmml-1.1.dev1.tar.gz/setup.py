#!/usr/bin/env python
#coding=utf-8

from setuptools import setup,find_packages
import io
import re

with io.open('cmml/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


setup(
    name="cmml",
    version=version,
    description=(
       "机器学习"
        ),
    long_description=open("README.rst").read(),
    author="曹明",
    author_email="18911205637@163.com",
    maintainer="曹明",
    maintainer_email='18911205637@163.com',
    license="BSD License",
    packages=find_packages(),
    pltforms=["all"],
    url="http://github.com/Mark110",
    classifiers=[
        #"Development Status :: 5 - Production/Stable',
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries"
        ],
    )

    
