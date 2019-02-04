#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: chenruitian
# Mail: chen-ruitian@163.com
# Created Time:  2019-01-30 16:25:34
#############################################


from setuptools import setup, find_packages

setup(
    name = "cninfowebapi",
    version = "0.1.1",
    keywords = ("pip", "cninfo","api", "cninfowebapi", "chenruitian"),
    description = "cninfo data platform webapi",
    long_description = "cninfo data platform api data, Including stock, fund, bond, futures, macroeconomic data, etc.",
    license = "MIT Licence",

    url = "https://github.com/chenruitian/cninfowebapi.git",
    author = "chenruitian",
    author_email = "chen-ruitian@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['pandas',"pymongo","python-dateutil"]
)