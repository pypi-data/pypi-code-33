#!/usr/bin/env python

from distutils.core import setup

setup(name='ybc_tuya',
      version='1.2.24',
      description='Turtle to draw.',
      long_description='Turtle to draw.',
      author='hurs',
      author_email='hurs@fenbi.com',
      keywords=['python', 'draw', 'turtle'],
      url='http://pip.zhenguanyu.com/',
      packages=['ybc_tuya'],
      package_data={'ybc_tuya': ['*.py']},
      license='MIT',
      install_requires='ybc_exception'
     )