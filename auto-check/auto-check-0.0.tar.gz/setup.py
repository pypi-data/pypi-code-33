#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='auto-check',
    version='0.0',
    description='主要用于针对使用E-Mobile自动打卡',
    long_description=open('README.rst').read(),
    author='一条肥鱼',
    author_email='sasuraiu@gmail.com',
    maintainer='一条肥鱼',
    maintainer_email='sasuraiu@gmail.com',
    license='MIT License',
    packages = find_packages('src'),
    platforms=["all"],
    url='https://github.com/sasuraiu/autocheck',
    package_dir={'':'src'},
    classifires = [
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'requests',
    ],
    entry_points = {
        'console_scripts':[
            'auto-check = auto_check.__main__:main'
        ]
    },
)