# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

#to publish
#python3 setup.py sdist 
#twine upload -r test dist/python-rpy-1.0.0.tar.gz 

import sys
import os
import codecs

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Software Development :: Libraries :: Password Manager"
]


def read(*rellibpath):
    try:
        with codecs.open(os.path.join(HERE, *rellibpath), 'r', encoding='utf-8') as fp:
              return fp.read()
    except FileNotFoundError:
        pass

def load_tests():
    from rpy.cli.commands.test import Command as TestCommand
    TestCommand().handle()

setup(
    name = 'python-rpy',
    version = '1.0.14',
    description = 'A Python library with various functional tools.',
    long_description = read('README.rst'),
    long_description_content_type = 'text/x-rst',
    keywords=['password'],
    author = 'Riccardo Di Virgilio',
    author_email = 'riccardodivirgilio@gmail.com',
    include_package_data=True,
    packages=find_packages(),
    test_suite='setup.load_tests',
    python_requires='>=3.5',
    install_requires = [

    ],
    project_urls={

    }
)
