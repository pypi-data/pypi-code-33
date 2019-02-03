#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 21:17:43 2019

@author: Maria Climent-Pommeret
"""
import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rnaviewparser",
    version="0.1.3",
    author="Maria Climent-Pommeret",
    author_email="maria@climent-pommeret.red",
    description="A RNAVIEW parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.climent-pommeret.red/Chopopope/rnaviewparser/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="RNA RNAVIEW parser",
    install_requires=[
            "ply",
            "pTable",
    ],
    python_requires='>=3.7',
)
