#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 21:17:43 2019

@author: Maria Climent-Pommeret
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parsetabtolatex",
    version="0.0.2",
    author="Maria Climent-Pommeret",
    author_email="maria@climent-pommeret.red",
    description="A parsetab.py parser that generates .tex file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.climent-pommeret.red/Chopopope/parsetabtolatex/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="ply grammar LaTeX parser",
    install_requires=[
            "ply",
    ],
    python_requires='>=3.5',
)
