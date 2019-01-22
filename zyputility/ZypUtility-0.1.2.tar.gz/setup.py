#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/22 9:31
# @Author  : Zhangyp
# @File    : setup.py
# @Software: PyCharm
# @license : Copyright(C), eWord Technology Co., Ltd.
# @Contact : yeahcheung213@163.com
# import (from .extractor import Document)

from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
	name="ZypUtility",
	version="0.1.2",
	author="Zhang Yeping",
	author_email="yeahcheung213@163.com",
	description="zyputility contains readconfig & log",
	long_description=open("README.rst").read(),
	license="MIT",
	url="https://github.com/cappuccino213/ZypUtility",
	packages=['ZypUtility'],
	install_requires=[],
	classifiers=[
		"Environment :: Web Environment",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Text Processing :: Indexing",
		"Topic :: Utilities",
		"Topic :: Internet",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
	],
)
