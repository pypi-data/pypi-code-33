#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
        name="rad2f5",
        version="2.0",
        packages=find_packages(),
        install_requires=['re'],
        author="Pete White",
        author_email="pwhite@f5.com",
        description="A Python script to convert RadWare configuration to F5 syntax",
        license="PSF",
        url="https://pypi.python.org/pypi?:action=display&name=rad2f5&version=2.0",
)
