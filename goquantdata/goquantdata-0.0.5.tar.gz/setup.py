import sys


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


if sys.version_info <= (2, 4):
  error = 'Requires Python Version 2.5 or above... exiting.'
  print >> sys.stderr, error
  sys.exit(1)


requirements = [
    'requests>=2.20.0,<3.0',
]

setup(name='goquantdata',
      version='0.0.5',
      description='Python client library for Go Quant Financial Data Services',
      scripts=[],
      url='https://github.com/hyu2707/goquant-data-client',
      packages=['goquantdata','goquantdata.local','goquantdata.local.db','goquantdata.local.datasource',
                'goquantdata.util'],
      #license='Apache 2.0',
      #platforms='Posix; MacOS X; Windows',
      setup_requires=requirements,
      install_requires=requirements,
      test_suite='goquantdata.test',
      # classifiers=['Development Status :: 4 - Beta',
      #              'Intended Audience :: Developers',
      #              'License :: OSI Approved :: Apache Software License',
      #              'Operating System :: OS Independent',
      #              'Programming Language :: Python :: 2.7',
      #              'Programming Language :: Python :: 3.2',
      #              'Programming Language :: Python :: 3.4',
      #              'Programming Language :: Python :: 3.5',
      #              'Programming Language :: Python :: 3.6',
      #              'Topic :: Internet',
      #              ]
      )