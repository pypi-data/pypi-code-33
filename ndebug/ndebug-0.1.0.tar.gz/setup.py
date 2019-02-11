#!/usr/bin/env python3
import re
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


with open('ndebug/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

with open('requirements/base.txt', 'r') as fd:
    requirements = fd.read().strip().split('\n')

setup(
    name='ndebug',
    version=version,
    description="Tiny python debugging utility like node.js debug module",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Malcom Gilbert, Peter Magnusson',
    author_email='peter@birchroad.se',
    url='https://github.com/kmpm/py-ndebug',
    license='MIT',
    packages=['ndebug'],
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)
