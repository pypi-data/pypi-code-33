#!/usr/bin/env python2
# coding=utf-8
"""Setup file for sshreader module"""

from setuptools import setup

setup(name='sshreader',
      version='4.5',
      description='Multi-threading/processing wrapper for Paramiko',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      url='http://sshreader.readthedocs.io/',
      project_urls={'Documentation': 'http://sshreader.readthedocs.io/',
                    'Source': 'https://bitbucket.org/isaiah1112/sshreader/',
                    'Tracker': 'https://bitbucket.org/isaiah1112/sshreader/issues'},
      packages=['sshreader'],
      include_package_data=True,
      scripts=['bin/pydsh'],
      install_requires=['click>=7.0',
                        'colorama>=0.4.1',
                        'future>=0.17.1',
                        'paramiko>=2.4.2',
                        'progressbar2>=3.39.2',
                        'python-hostlist==1.18',
                        ],
      platforms=['Linux', 'Darwin'],
      classifiers=[
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      )
