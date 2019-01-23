#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup
from setuptools.command.install import install

VERSION = "0.1.1"

def parse_requirements(filename):
  """ load requirements from a pip requirements file """
  lineiter = (line.strip() for line in open(filename))
  return [line for line in lineiter if line and not line.startswith('#')]

with open('README.md', 'r') as fh:
  long_description = fh.read()

class VerifyVersionCommand(install):
  """Custom command to verify that the git tag matches our version"""
  description = 'verify that the git tag matches our version'

  def run(self):
    tag = os.getenv('CIRCLE_TAG')

    if tag != VERSION:
      info = "Git tag: {0} does not match the version of this app: {1}".format(
        tag, VERSION
      )
      sys.exit(info)

setup(
  name='ELSPy',
  version=VERSION,
  packages=['ELSPy'],
  author='Miikka Värri',
  author_email='miikka.varri@gmail.com',
  description='Electrolux Laundry System Python utility package',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/ruuti/ELSPy',
  install_requires=parse_requirements('requirements.txt'),
  platforms='any',
  python_requires='>=3',
  classifiers=[
     'Programming Language :: Python :: 3',
     'License :: OSI Approved :: MIT License',
     'Operating System :: OS Independent',
  ],
  cmdclass={
    'verify': VerifyVersionCommand,
  }
 )