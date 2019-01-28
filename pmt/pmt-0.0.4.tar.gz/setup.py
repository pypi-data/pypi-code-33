#!/usr/bin/env python

import re


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = '0.0.4'

if not version:
    raise RuntimeError('Cannot find version information')


with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='pmt',
	author='Jiao Shuai',
	author_email='jiaoshuaihit@gmail.com',
    version=version,
    description='pmt (Lovearth Python Multi-threading ) SDK',
    long_description=readme,
    packages=['pmt'],
    install_requires=[],
    include_package_data=True,
    url='http://pmt.xdua.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)

