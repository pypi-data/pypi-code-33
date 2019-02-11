# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:50:29 2018

@author: yili.peng
"""

from setuptools import setup
from pypandoc import convert_file

setup(name='RNWS'
      ,version='0.2.1'
      ,description='read and write daily stock data'
      ,long_description=convert_file('README.md', 'rst', format='markdown_github').replace("\r","")
      ,author='Yili Peng'
      ,author_email='yili_peng@outlook.com'
      ,packages=['RNWS']
      ,package_data={
		'RNWS': ['data/trading_date.csv'],
		}
      ,zip_safe=False)