# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setup
   Description :
   Author :       潘晓华
   date：          2019/1/15
-------------------------------------------------
"""


from setuptools import find_packages, setup


CLIENT_VERSION = "0.1.1"
PACKAGE_NAME = 'cloud-sdk'

def extract_requirements(filename):
    with open(filename, 'r') as requirements_file:
        return requirements_file.read().splitlines()
setup(
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    description='该库主要是封装了cloud Iaas的API，进行方便获取与操作IaaS资源',
    author_email='pxhua@aliyun.com',
    author='xhua',
    url="https://github.com/xhuaustc/cloud-sdk.git",
    keywords=['Qingcloud', 'Iaas'],
    install_requires=extract_requirements('requirements.txt'),
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('requirements.txt', ['requirements.txt']),
    ]
)
