#!/usr/bin/env python

import sys
import os
from setuptools import setup, find_packages


"""
INSTALLATION
1. Check if PyPi credentials file called .pypirc is created locally. If not, create it.
2. Increase the number of version in    setup.py file
3. In pypanabi folder, run sudo python setup.py sdist upload
4. Uninstall old version of pypanabi-tools by running sudo -H pip uninstall pypanabi-tools
5. Install last version from PyPi sudo pip install -U pypanabi-tools
"""

name = "pypanabi-tools"
rootdir = os.path.abspath(os.path.dirname(__file__))

# Python 2.4 or later needed
if sys.version_info < (2, 4, 0, 'final', 0):
    raise SystemExit

setup(
    name=name,
    version='1.9.82',
    description='Shared Python functions for OLX Business Intelligence Team',
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],
    keywords='olx bi panamera',
    author='OLX',
    author_email='panamera-bi@olx.com',
    packages=find_packages(),
    install_requires=[
        'findspark',
        'boto3',
        'psycopg2',
        'pymysql',
        'sqlparse',
        'click',
        'ijson',
        'ConfigParser',
        'logging',
        'fastparquet',
        'python-dateutil',
        'requests',
        'urllib3',
        'pytz',
        'numpy',
        'urllib3',
        'python-jenkins',
        'facebook-sdk'
    ],
    include_package_data=True,
    zip_safe=False
)
