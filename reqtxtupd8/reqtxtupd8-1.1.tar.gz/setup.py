#!/usr/bin/env python

"""
This is my first distribution :)
"""

from setuptools import setup

setup(name='reqtxtupd8',
      version='1.1',
      description='Writes your package list to requirements.txt',
      author='Edgar Mamerto',
      author_email='edmamerto@gmail.com',
      url='https://github.com/edmamerto/reqtxtupd8',
      packages=['reqtxtupd8'],
      entry_points={
          'console_scripts': [
              'requpd8=reqtxtupd8:run'
          ]
      }
     )
