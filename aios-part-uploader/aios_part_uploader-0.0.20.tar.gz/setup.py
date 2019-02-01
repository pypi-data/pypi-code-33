#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: shawn
# Mail: wang.xiao@intellif.com
# Created Time:  2018-12-17 15:20:34
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "aios_part_uploader",      #这里是pip项目发布的名称
    version = "0.0.20",  #版本号，数值大的会优先被pip
    keywords = ("aios", "part", "uploader"),
    description = "aios part uploader",
    long_description = "aios part uploader",
    license = "MIT Licence",

    url = "https://github.com/wangxiao1427/python_helper/tree/master/aios_part_uploader",     #项目相关文件地址，一般是github
    author = "shawn_wg",
    author_email = "wang.xiao@intellif.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []          #这个项目需要的第三方库
)