#!/usr/bin/env python
from setuptools import setup, find_packages
import nbtest

with open("README.md", "r") as fh:
    long_description = fh.read()

desc = """nbtest
========

that supports Python 2.7
Usage
'''''
now just used by myself

"""

setup(
    name = 'nbtest',
    packages = ['nbtest'],
    version = nbtest.__version__,
    description = 'nbtest',
    long_description = desc,
    author = 'jayvee-yjw',
    author_email = 'gmkingyao001@gmail.com',
    url = 'https://github.com/jayvee-yjw/nbtest',
    download_url = 'https://github.com/jayvee-yjw/nbtest/archive/master.zip',
    keywords=["nbtest"],
    zip_safe=True,
    install_requires=['assertpy', 'jsonpath_rw_ext']
)