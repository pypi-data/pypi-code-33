#!/usr/bin/env python
from setuptools import setup, find_packages

#version number
version = '0.1.7'

entry_points = {
    'console_scripts': [
        'k3 = kea3.cli:dispatch',
    ]}


setup(name='kea3',
      version=version,
      description='file metadata tracker',
      author='Mark Fiers',
      author_email='mark.fiers.42@gmail.com',
      entry_points = entry_points,
      url='https://gitlab.com/mf42/kea3',
      packages=find_packages(),
      package_data={'kea3': ['etc/*.config']},
      install_requires=[
          'fantail',
          'humanfriendly',
          'networkx',
          'base58',
          'sqlalchemy',
          'pytz',
          'psutil',
          'path.py',
          'arrow',
          'pytest',
          'psycopg2-binary',
    ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ]
)
