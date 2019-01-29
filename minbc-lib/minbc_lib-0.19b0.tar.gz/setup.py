#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from minbc_lib import __version__
from setuptools import setup, find_packages

try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = __version__

setup(
    name="minbc_lib",
    version=version,
    url='https://github.com/shibats/minbc_lib',
    author='ats',
    author_email='shibata@m-info.co.jp',
    maintainer='ats',
    maintainer_email='shibata@m-info.co.jp',
    description='Package Dependency: Validates package requirements',
    long_description=readme,
    packages=find_packages(),
    install_requires=['pyenigma'],
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      pkgdep = pypipkg.scripts.command:main
    """,
)