# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="dance",
    version="0.0.1",
    author="Aareon Sullivan",
    author_email="askully13@gmail.com",
    description="A cross-platform desktop application development library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aareon/dance",
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