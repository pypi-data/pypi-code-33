#!/usr/bin/env python
# encoding: utf-8

from setuptools import (setup, find_packages)

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="qwert",
    version="2.0.0",
    packages=find_packages(),

    # metadata for upload to PyPI
    author="Vision Network",
    author_email="michael@vision.network",
    description="Python extensions: list/dict/file...",
    keywords='Python, Extensions, List, Dict, File',

    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VisionNetworkProject/python-qwert",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        'cli-print',
        'requests',
        'pyperclip',
    ],
)
