# -*- coding: utf-8 -*-
"""
Created on Fri May 18 13:56:46 2018

@author: yili.peng
"""


from setuptools import setup
from pypandoc import convert_file

setup(name='alpha_factory'
      ,version='0.3.6'
      ,description='generate alpha factors'
      ,long_description=convert_file('README.md', 'rst', format='markdown_github').replace("\r","")
      ,lisence='MIT'
      ,author='Yili Peng'
      ,author_email='yili_peng@outlook.com'
      ,packages=['alpha_factory']
      ,install_requires=[
          'RNWS>=0.2.1',
          'single_factor_model>=0.3.2',
          'data_box',
          'alphalens',
          'empyrical'
      ]
      ,package_data={
        'alpha_factory': ['data/functions.csv'],
        }
      ,zip_safe=False)