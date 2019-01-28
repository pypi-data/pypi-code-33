#!/usr/bin/env python

import re


try:
    from setuptools import setup,find_packages
except ImportError:
    from distutils.core import setup

version = '0.3.3'

found_packages = find_packages(exclude=["doc","examples","test"])


if not version:
    raise RuntimeError('Cannot find version information')


with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

setup(
    name='wccqcc',
	author='Jiao Shuai',
	author_email='jiaoshuaihit@gmail.com',
    version=version,
    description='Wikicivi WCC Qichacha',
    long_description=readme,
    packages=found_packages,
    install_requires=['requests!=2.9.0','wcc>=1.7.0','tqdm','lxml','pymongo','beautifulsoup4','pmt','comcom'],
    include_package_data=True,
    url='http://wccqcc.wikicivi.com',
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
        'Programming Language :: Python :: 3.6'
    ],
)

