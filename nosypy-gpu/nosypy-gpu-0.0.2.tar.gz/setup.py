#!/usr/bin/env python
""" NosyPy is a self supervised novelty detection package built for time lapse imagery using Python.

    - It is built ontop of Tensorflow 
    - It uses a self supervised learning approach, removing the need for manual annotation
    - It identifies areas in each image which likely contain an object, or objects, of interest   
"""

from distutils.core import setup
from setuptools import find_packages

DOCLINES = (__doc__ or '').split("\n")

setup(name='nosypy-gpu',
      version='0.0.2',
      description=DOCLINES[0],
      long_description="\n".join(DOCLINES[0:]),
      url='http://github.com/brett-hosking/nosypy',
      license='MIT',
      author='brett hosking',
      author_email='wilski@noc.ac.uk',
      install_requires=[
                "tensorflow-gpu>=1.12.0",
                "requests>=2.21.0",
                "imageio>=2.5.0",
                "scipy>=1.2.0",
                "scikit-image>=0.14.2"
                ],
      packages=find_packages()
      )
