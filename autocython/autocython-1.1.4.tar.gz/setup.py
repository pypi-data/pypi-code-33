#!/usr/bin/env python

# To upload a version to PyPI, run:
#
#    python setup.py sdist upload
#
# If the package is not registered with PyPI yet, do so with:
#
# python setup.py register

from setuptools import setup
import os

VERSION = '1.1.4'

# Auto generate a __version__ package for the package to import
with open(os.path.join('autocython', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n"%VERSION)

setup(name='autocython',
      version=VERSION,
      description="Automatic cython compilation with multiplatform support.",
      author='Chris Billington',
      author_email='chrisjbillington@gmail.com',
      url='https://bitbucket.org/cbillington/autocython/',
      license="BSD",
      packages=['autocython'],
      install_requires=['cython']
     )
