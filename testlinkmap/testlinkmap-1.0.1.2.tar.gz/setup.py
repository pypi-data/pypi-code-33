#! /usr/local/bin/python3

from setuptools import setup

setup(
      name              = 'testlinkmap',
      version           = '1.0.1.2',
      description       = 'find macho linkmap and output otool sections',
      url               = '',
      author            = 'LiTing',
      author_email      = 'match.lt@alibaba-inc.com',
      license           = 'MIT',
      classifiers       = [
                              'License :: OSI Approved :: MIT License',
                              'Operating System :: OS Independent',
                              'Programming Language :: Python :: 3',
                              'Programming Language :: Python :: 3.6',
                              'Programming Language :: Python :: 3.7',
                              ],
      keywords          = 'linkmap macho python',
      packages          = ['testlinkmap', 'testlinkmap.utils'],
      )
