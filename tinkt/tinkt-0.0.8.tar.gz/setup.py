# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="tinkt",
    version="0.0.8",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="color and colormap utils (for matplotlib)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claydodo/tinkt",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7 ",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'konfluence >= 0.0.1',
        'krux',
    ]
)
