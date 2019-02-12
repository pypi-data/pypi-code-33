#!/usr/bin/env python

from distutils.core import setup

setup(name='ybc_browser',
      version='1.0.11',
      description='Open web browser.',
      long_description='Open web browser',
      author='lijz01',
      author_email='lijz01@fenbi.com',
      keywords=['python', 'browser'],
      url='http://pip.zhenguanyu.com/',
      packages=['ybc_browser'],
      package_data={'ybc_browser': ['__init__.py', 'ybc_browser.py', 'ybc_browser_unitest.py']},
      license='MIT',
      install_requires=['pypinyin', 'ybc_exception']
     )