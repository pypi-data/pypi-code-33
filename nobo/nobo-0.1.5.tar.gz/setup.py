#!/usr/bin/env python

from distutils.core import setup

setup(name='nobo',
      version='0.1.5',
      description='A third-party Rits API',
      long_description='A third-party spider that you could get your data from each service provides by Ritsumeikan University',
      author='Zhou Fang',
      license='GPLv3',
      author_email='is0385rx@ed.ritsumei.ac.jp',
      url='https://github.com/fang2hou/Nobo',
      packages=['nobo'],
      keywords = ['ritsumei', 'manaba'],
      python_requires='>=3.4',
      install_requires=[
        "beautifulsoup4",
        "selenium",
      ],
     )