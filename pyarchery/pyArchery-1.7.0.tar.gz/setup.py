#!/usr/bin/env python

import ast
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'archery', '__init__.py'), 'rb') as f:
    version = str(ast.literal_eval(re.search(r'__version__\s*=\s*(.*)', f.read().decode('utf-8')).group(1)))

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='pyArchery',
    packages=[
        'archery',
    ],
    version=version,
    description='Python library enumerating the Archery Tool RESTFul API endpoints.',
    long_description=readme,
    author='Anand Tiwari',
    author_email='anandtiwarics@gmail.com',
    url='https://github.com/archerysec/',
    download_url='',
    license='MIT License',
    zip_safe=True,
    install_requires=['requests'],
    keywords=['pyArchery', 'api', 'security', 'software', 'ArcherySec'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
    ]
)
