#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Noskcaj19",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Utilities for building frc robots",
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[
        "pynetworktables",
        "robotpy-wpilib-utilities",
        "robotpy-hal-base",
        "wpilib",
    ],
    license="License :: OSI Approved :: MIT License",
    include_package_data=True,
    name="marsutils",
    packages=find_packages(include=["marsutils"]),
    url="https://github.com/Mars1523/Mars-Utils",
    version="0.4.0",
)
