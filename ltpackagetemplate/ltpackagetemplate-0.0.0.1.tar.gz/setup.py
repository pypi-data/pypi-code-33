#! /usr/local/bin/python3

from setuptools import setup

setup(
      name              = 'ltpackagetemplate',
      version           = '0.0.0.1',
      description       = 'package template',
      url               = '',
      author            = 'LiTing',
      author_email      = '',
      license           = 'MIT',
      classifiers       = [
                              'License :: OSI Approved :: MIT License',
                              'Operating System :: OS Independent',
                              'Programming Language :: Python :: 3',
                              'Programming Language :: Python :: 3.6',
                              'Programming Language :: Python :: 3.7',
                              ],
      keywords          = 'package template',
      packages          = ['ltpackagetemplate', 'ltpackagetemplate.utils'],
      )
