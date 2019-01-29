#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Yehuaqing
# Mail: yhq@zhejiangit.com
# Created Time:  2019-01-29
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "pweb",      #这里是pip项目发布的名称
    version = "1.2.1",  #版本号，数值大的会优先被pip
    keywords = ("pip", "pweb","pyweb"),
    description = "An small python web framework",
    long_description = "An small python web frame work",
    license = "MIT Licence",

    url = "https://www.zhejiangit.com/pwebapp/",     #项目相关文件地址，一般是github
    author = "Yehuaqing",
    author_email = "yhq@zhejiangit.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    scripts=['scripts/pweb-admin.py'],
    install_requires = ["pymssql"]          #这个项目需要的第三方库
)
