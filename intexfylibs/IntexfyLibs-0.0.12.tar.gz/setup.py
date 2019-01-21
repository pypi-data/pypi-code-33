# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# from distutils.core import setup

setup(
    name='IntexfyLibs',
    version='0.0.12',
    author='Heitor Tancredo',
    author_email='heitor@intexfy.com',
    keywords='Intexfy Libs',
    description='Package with intexfy libs',
    install_requires=['datetime'],
    packages=find_packages(),
)
