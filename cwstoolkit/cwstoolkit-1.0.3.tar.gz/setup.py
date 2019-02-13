#!/usr/bin/env python
#encoding: utf-8
#

from __future__ import print_function
from setuptools import setup, find_packages
import sys


setup(
	name = "cwstoolkit",
	version = "1.0.3",
	author = "Colin",
	author_email = "colinspace@126.com",
	description = "colinspace smart-devops toolkits",
	long_description = open("README.rst").read(),
	license = "MIT",
	url = "https://github.com/opscolin/colinspace",
	platforms = "Linux, Unix, Mac",
	keywords = "colinspace, Colin, python, toolkits,colinws",
	packages = ["cwstoolkit"],
	install_requires = ['yunpian_python_sdk','aliyun-python-sdk-core-v3','aliyun-python-sdk-dysmsapi','qiniu']
)
	
