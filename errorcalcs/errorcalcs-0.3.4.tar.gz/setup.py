# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='errorcalcs',
    version='0.3.4',
    description='GUI for error calulations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leonfrcom/ErroRCalcS",
    author='lefrcom',
    author_email='lefrcom@gmx.de',
    packages=['errorcalcs'],
    install_requires=[
              'uncertainties',
              'PyQt5'
              ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
)
