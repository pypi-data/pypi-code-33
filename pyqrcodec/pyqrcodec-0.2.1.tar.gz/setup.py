#! /usr/bin/python
# -*- coding: UTF-8 -*-
#
from setuptools import setup, find_packages
# http://www.cnblogs.com/sting2me/p/6550897.html

PACKAGE = "pyqrcodec"
NAME = "pyqrcodec"
DESCRIPTION = "pyqrcodec 是一个用于探索QR码生成原理而编写的python包。它实现了QR码生成过程中的底层逻辑，以0、1序列的字符串代表待编码数据，更直观、更加方便理解。"
AUTHOR = "cosimzhou"
AUTHOR_EMAIL = "cosimzhou@hotmail.com"
URL = "https://github.com/Cosimzhou/pyqrcode"
VERSION = __import__(PACKAGE).__version__
 
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=DESCRIPTION,#read("README.rst"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests"]),
    # package_data=find_package_data(
    #         PACKAGE,
    #         only_in_packages=False
    #   ),
    install_requires=[
        'Pillow>=3.4.2',
    ],
    zip_safe=False,
)