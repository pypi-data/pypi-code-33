#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import basename, splitext

from glob import glob
from setuptools import setup
from setuptools import find_packages


__version__ = '0.4.1'


with open('README.rst') as readme_file:
    readme = readme_file.read()


setup_options = {
    'name': 'conficus',
    'version': __version__,
    'description': "ini config library",
    'long_description': readme,
    'author': "Mark Gemmill",
    'author_email': 'mark@markgemmill.com',
    'url': 'http://thebitsilo.com/dev/conficus/current',
    'download_url': 'https://bitbucket.org/mgemmill/conficus',
    'packages': find_packages(where='src'),
    'package_dir': {'': 'src'},
    'py_modules': [splitext(basename(i))[0] for i in glob("src/*.py")],
    'include_package_data': True,
    'zip_safe': False,
    'keywords': 'conficus ini configurtion',
    'install_requires': ['pathlib2 >= 2.3.0;python_version<"3.4"'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'
    ]}


setup(**setup_options)
