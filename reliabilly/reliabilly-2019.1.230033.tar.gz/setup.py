#!/usr/bin/env python
from setuptools import setup, find_packages
from settings import SetupSettings

# pragma: no cover
setup(name=SetupSettings.PACKAGE_NAME,
      version=SetupSettings.VERSION,
      python_requires=SetupSettings.PYTHON_REQUIRES,
      install_requires=SetupSettings.REQUIREMENTS,
      description=SetupSettings.DESCRIPTION,
      author=SetupSettings.AUTHOR,
      author_email=SetupSettings.AUTHOR_EMAIL,
      include_package_data=True,
      license=SetupSettings.LICENSE,
      packages=find_packages(exclude=SetupSettings.EXCLUDE_MODULES),)
