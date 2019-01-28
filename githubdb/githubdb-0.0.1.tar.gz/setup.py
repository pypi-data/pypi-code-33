#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup

setup(
    name='githubdb',
    version='0.0.1',
    author='dancerNight',
    author_email='zyzhang2.zz@gmail.com',
    url='https://github.com/zyzhang2-zz/githubdb/',
    description='',
    packages=['githubdb'],
    install_requires=["PyGithub", "requests"],
    entry_points={
        'console_scripts': []
    }
)