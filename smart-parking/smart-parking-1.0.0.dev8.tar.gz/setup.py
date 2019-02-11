from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools import find_packages
from os import path

import os
import re
import json

pkg_name = "smart-parking"
version = "1.0.0.dev8"
# read the contents of your README file

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name=pkg_name,
	version=version,
	author="Jonathan Martins Sandri",
	description="Smart Parking",
	long_description='Smart Parking',
	long_description_content_type="text/markdown",
	url="https://bitbucket.org/jonathanmartinssandri/managersmartparking.git",
 	packages=find_packages(),
	package_data={
		'': ['*.xml','*.json']
	},
	install_requires=[
		'watchtower==0.5.4',
        'opencv-python',
		'numpy',
		'yaml'
	]
)
