# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
from cropper import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name="harvest-cropper",
      author="Jorge Sanz",
      author_email="jsanz@carto.com",
      description="An app to explore Harvest data",
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      keywords="harvest api",
      license="BSD",
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
      ],
      version=VERSION,
      url="https://github.com/CartoDB/cropper",
      install_requires=[
          "requests==2.21.0",
          "Click==7.0"
      ],
      packages=find_packages(),
      include_package_data=True,
      entry_points='''
[console_scripts]
cropper=cropper.cli:cli
      '''
      )
