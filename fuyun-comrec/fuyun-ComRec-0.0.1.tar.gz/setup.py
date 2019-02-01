#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: wangyilang
# Mail: wylkowe@qq.com
# Created Time:  2019-01-30 17:15:21

# 打包:python setup.py sdist upload -r privatepypi
# 安装: pip install -i http://172.16.70.200:3141 fuyun-company-ner --trusted-host 172.16.70.200
#############################################

from setuptools import setup, find_packages

setup(
    name = "fuyun-ComRec",      #pip项目发布的名称
    version = "0.0.1",  #版本号，数值大的会优先被pip
    keywords = ["pip", "company","ner","fuyun"],
    description = "福韵公司字号提取项目",
    long_description = "公司字号提取",

    url = "https://github.com/wyl-nlp/ComRec", #项目相关文件地址
    author = "wangyilang",
    author_email = "wylkowe@qq.com",
    packages=find_packages(),
    include_package_data = True,
    platforms = "any",
    classifiers=['Topic :: Utilities', 'Programming Language :: Python :: 3.6'],
    install_requires = ['pandas>=0.23.4', 'tensorflow>=1.12.0', 'numpy>=1.14.3']#这个项目需要的第三方库
)
