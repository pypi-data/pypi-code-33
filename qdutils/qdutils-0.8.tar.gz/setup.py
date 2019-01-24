# -*- coding:utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(name='qdutils',
      version='0.8',
      # packages=find_packages(where='./src/'),  # 查找包的路径
      packages=find_packages(),
      # package_dir={'': 'src'},
      include_package_data=False,
      # package_data={'data': []},
      description='python common utils',
      long_description='',
      author='tony',
      author_email='874404359@qq.com',
      url='https://github.com/qdutils',  # homepage
      # license='MIT',
      install_requires=[],
      classifiers=[
          "Programming Language :: Python :: 2",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      )
