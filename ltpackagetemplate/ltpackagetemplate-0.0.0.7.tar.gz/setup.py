#! /usr/local/bin/python3

from setuptools import setup

setup(
      name              = 'ltpackagetemplate',  # 包名
      version           = '0.0.0.7',            # 版本号
      description       = 'package template',   # 描述
      url               = '',                   # 源码地址
      author            = 'LiTing',             # 作者
      author_email      = '',                   # 邮箱
      license           = 'MIT',
      classifiers       = [
                              'License :: OSI Approved :: MIT License',
                              'Operating System :: OS Independent',
                              'Programming Language :: Python :: 3',
                              'Programming Language :: Python :: 3.6',
                              'Programming Language :: Python :: 3.7',
                              ],
      keywords          = 'package template',   # 关键词标签
      packages          = ['ltpackagetemplate', 'ltpackagetemplate.utils'], # 包代码
      )