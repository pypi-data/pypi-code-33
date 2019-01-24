# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="syntect",
    version="0.0.1",
    author="Aareon Sullivan, Tristan Hume, and others",
    author_email="askully13@gmail.com",
    description="A Python binding for the Syntect library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aareon/python-syntect",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "setuptools >= 30.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)