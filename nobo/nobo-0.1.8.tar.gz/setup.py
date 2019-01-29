#!/usr/bin/env python

from distutils.core import setup

setup(name='nobo',
      version='0.1.8',
      description='A data spider for Ritsmeikan Univ.',
      long_description='A spider for fetching data from Manaba+R & CampusWeb. (Ritsumeikan Univ.)',
      author='Zhou Fang',
      license='GPLv3',
      author_email='is0385rx@ed.ritsumei.ac.jp',
      url='https://github.com/fang2hou/nobo',
      packages=['nobo'],
      keywords = ['ritsumei', 'manaba'],
      python_requires='>=3.4',
      install_requires=[
        "beautifulsoup4",
        "selenium",
      ],
     )