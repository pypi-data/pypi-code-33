# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:21:09 2018

@author: yili.peng
"""

from setuptools import setup
from pypandoc import convert_file

setup(name='single_factor_model'
      ,version='0.3.0a'
      ,description='factor model'
      ,long_description=convert_file('README.md', 'rst', format='markdown_github').replace("\r","")
      ,lisence='MIT'
      ,author='Yili Peng'
      ,author_email='yili_peng@outlook.com'
      ,packages=['single_factor_model']
      ,install_requires=[
          'empyrical',
          'data_box'
      ]
      ,zip_safe=False)