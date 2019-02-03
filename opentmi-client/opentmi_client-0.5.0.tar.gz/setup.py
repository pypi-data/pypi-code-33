#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2018 by Jussi Vatjus-Anttila
:license: MIT, see LICENSE for more details.
"""
import os
import sys
from distutils.core import setup
from setuptools import find_packages
from setuptools.command.install import install

DESCRIPTION = "opentmi-client"
OWNER_NAMES = 'Jussi Vatjus-Anttila'
OWNER_EMAILS = 'jussiva@gmail.com'
VERSION = '0.5.0'

# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')
        version = "v" + VERSION
        if tag != version:
            info = "Git tag: {0} does not match the"\
            "version of this app: {1}".format(tag, version)
            sys.exit(info)

setup(name='opentmi_client',
      version=VERSION,
      description=DESCRIPTION,
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/OpenTMI/opentmi-pyclient.git',
      packages=find_packages(exclude=['test', 'log', 'htmlcov', 'docs']),
      include_package_data=True,
      license="MIT",
      tests_require=[
          "coverage",
          "mock",
          "pylint",
          "Sphinx",
          "nose"
      ],
      test_suite='test',
      keywords='opentmi ci cd api sdk',
      entry_points={
          "console_scripts": [
              "opentmi=opentmi_client:opentmiclient_main",
          ]
      },
      install_requires=[
          "requests>=2.13.0",
          "jsonmerge",
          "six",
          "pydash",
          "junitparser"
      ],
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      cmdclass={
          'verify': VerifyVersionCommand,
      }
     )
