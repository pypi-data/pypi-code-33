#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author="Mark Lee",
    author_email='mark@droveend.com',
    description="Converts an Evernote export to an emacs org-mode document",
    entry_points={
        'console_scripts': [
            'orgenex=orgenex:cli'
        ],
    },
    install_requires=[
        'Click',
        'lxml'
    ],
    long_description=f'{readme}',
    include_package_data=True,
    keywords='org-mode emacs evernote pandoc',
    name='orgenex',
    packages=find_packages(),
    url='https://bitbucket.org/tipmethewink/orgenex',
    version='0.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ]
)
