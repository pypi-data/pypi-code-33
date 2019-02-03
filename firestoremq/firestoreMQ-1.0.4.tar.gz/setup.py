#!/usr/bin/env python3

from distutils.core import setup
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='firestoreMQ',
      version='1.0.4',
      description='Firestore MQ python library',
      author='Alex Robinson',
      author_email='alex@arrx.uk',
      packages=find_packages(),
      long_description=long_description,
      url='https://gitlab.com/a-robinson/firestoremq',
      long_description_content_type="text/markdown",
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)