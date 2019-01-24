#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(
    name='biolxyUtil',
    version='0.0.3',
    author='biolxy, codeunsolved',
    author_email='biolxy@aliyun.com',
    maintainer='biolxy',
    maintainer_email='biolxy@aliyun.com',
    url='https://pypi.org/project/biolxyUtil/',
    packages=['biolxyUtil'],
    platforms=["all"],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'getcpuNumber=biolxyUtil:getcpuNumber',
            'color_term=biolxyUtil:color_term',
            'execute_cmd=biolxyUtil:execute_cmd',
            'execute_cmd2=biolxyUtil:execute_cmd2',
            'diff_multiple_list=biolxyUtil:diff_multiple_list',
            'getDictbyListFromFasta=biolxyUtil:getDictbyListFromFasta',
            'getTranslatePep=biolxyUtil:getTranslatePep',
            'get_real_path=biolxyUtil:get_real_path',
            'getFile=biolxyUtil:getFile',
            'progressBar=biolxyUtil:progressBar',
            'progressBar2=biolxyUtil:progressBar2'
        ]
    },
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)