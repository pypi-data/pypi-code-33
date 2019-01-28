#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: JunWang
# Mail: shutupwj@163.com
# Created Time:  2018-6-8 11:30:34
#############################################

from setuptools import setup, find_packages

setup(
    name = "Jskit",
    version = "0.2.1",
    keywords = ("pip", "tool kit"),
    description = "A personal tool kit",
    long_description = "A personal tool kit",
    license = "Apache License Version 2.0",

    url = "https://github.com/Jakkwj/Jskit",
    author = "JunWang",
    author_email = "shutupwj@163.com",

    packages = find_packages(),
    # packages = find_packages(''),
    # package_dir = {'':''},   
    # package_data = {'': ['*.xlsx']},
    include_package_data = True,
    exclude_package_data = {'': ['.gitignore'], '': ['*.m']}, 
    platforms = "any",
    install_requires = ["selenium", "pyautogui"]
)
