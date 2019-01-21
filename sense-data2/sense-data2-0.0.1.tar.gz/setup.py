#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved
File: {name}.py
Author: xuwei
Email: weix@sensedeal.ai
Last modified: 2018.12.23
Description:
'''

from setuptools import setup, find_packages

requirements = [
    "grpcio",
    "grpcio-tools",
    "sense-core",
    "datetime",
]

# with open("README.md", "r") as fh:
#     long_description = fh.read().encode("bytes")

setup(
    name='sense-data2',
    version='0.0.1',
    packages=['sense_data2'],
    #packages=find_packages('sense_data2'),  # 包含所有sense_data中的包
    #package_dir = {'':'sense_data2'},   # 告诉distutils包都在sense_data下
    include_package_data = True,
    install_requires=requirements,


    license='XW License',  # example license
    author='xw20181227',
    author_email='weix@sensedeal.ai',
    description='stock information',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    #keywords = '',
    #url = '',
)