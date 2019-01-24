#! /usr/bin/env python3
"""Pyxigen Setup."""

from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="pyxidoc",
    version="0.1.dev2",
    author="merigor",
    author_email="",
    description="Very simple API documentation generator written in Python3.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="http://github.com/merigor/pyxidoc",
    license="MIT",
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
