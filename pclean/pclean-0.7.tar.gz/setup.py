#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Mark Lee",
    author_email='mark@droveend.com',
    description="Find and remove duplicate files in a pCloud account",
    entry_points={
        'console_scripts': [
            'pclean=pclean:cli'
        ],
    },
    install_requires=[
        'Click',
        'pcloud',
        'tqdm'
    ],
    long_description=f'{readme}',
    include_package_data=True,
    keywords='pcloud duplicate',
    name='pclean',
    packages=find_packages(
        include=['pclean']
    ),
    url='https://bitbucket.org/tipmethewink/pclean',
    version='0.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ]
)
