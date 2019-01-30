#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md") as rm_file:
    long_description = rm_file.read()

setup(
    name='domophoenix',
    version='0.2.1',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.domo.com',
    license='SEE LICENSE',
    author='John Woodruff',
    author_email='johnwoodruff91@gmail.com',
    description='Create beautiful Domo Phoenix charts with Python in Jupyter'
)
