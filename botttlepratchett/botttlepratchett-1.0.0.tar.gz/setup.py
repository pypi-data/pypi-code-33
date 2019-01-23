#!/usr/bin/env python

import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='botttlepratchett',
      version='1.0.0',
      description='A middleware for Bottle that provides GNU Terry Pratchett',
      long_description = long_description,
      long_description_content_type="text/markdown",
      author='James Milne',
      author_email='james.milne@protonmail.com',
      url='https://git.sr.ht/~shakna/bottlepratchett',
      py_modules=['bottlepratchett'],
      install_requires=['bottle>=0.12.1'],
      packages=setuptools.find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
     ],
     )
