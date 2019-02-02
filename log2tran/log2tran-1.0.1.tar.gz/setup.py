#!/usr/bin/env python

import re
import setuptools

version = ""
with open('__init__.py', 'r') as fd:
  version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
            fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name = "log2tran",
  version = version,
  py_modules = ['log2tran'],
  author = "Aaron Tang",
  author_email = "justforfun2000@msn.com",
  url = "https://gz.echase.cn/",
  description = "A simple program to parse BMP log files",
  long_description=long_description,
#  long_description_content_type="text/markdown",
  install_requires=[
#    'requests!=2.9.0',
#    'lxml>=4.2.3',
#    'monotonic>=1.5',
  ],
  packages=setuptools.find_packages(exclude=("log")),
  classifiers=[
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
  ],
#  exclude_package_data={'': ["example-pkg/test.py", "example-pkg/config.txt"]},
)
