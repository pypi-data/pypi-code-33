#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
File:   setup.py
Author: Lijiacai (1050518702@qq.com)
Date: 2019-02-03
Description:
   setup tool
"""

import os
import sys

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)

from setuptools import setup
from setuptools import find_packages
try:
    des = "  "
    with open("long_desciption.py", "r") as f:
	for i in f:
	    des = des + "  " + str(i) + "\n" 
except Exception as e:
    pass

setup(
    name="Producer_Consumer",
    version="19.6",
    keywords=("Queue", "queue", "Producer_Consumer", "producer_consumer", "producer", "consumer", "process"),
    description="producer and consumer models",
    long_description=des,
    license="MIT License",

    url="https://github.com/lijiacaigit/Producer_Consumer",
    author="Lijiacai",
    author_email="1050518702@qq.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["multiprocessing"]  # 这个项目需要的第三方库
)
