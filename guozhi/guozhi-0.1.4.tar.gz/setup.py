#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from setuptools import setup, find_packages

long_description = ''
if os.path.exists("PIP_README.md"):
    with open("PIP_README.md", "r") as fh:
        long_description = fh.read()
setup(
    name="guozhi",
    version="0.1.4",
    author="yebing",
    author_email="cui_com@qq.com",
    maintainer_email="cui_com@qq.com",
    description="python-iot-sdk for guozhiyun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/cui_com/jucie-python-sdk.git",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        'paho-mqtt>=1.4.0'
    ],
    zip_safe=False
)
