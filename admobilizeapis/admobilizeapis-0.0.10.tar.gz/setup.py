""" Setup module for AdMobilizeAPIs

See:
https://www.bitbucket.org/admobilize/admobilizeapis
"""

import setuptools

from setuptools import setup, find_packages

install_requires = [
  'google-api-core >= 1.6.0, < 1.8',
  'protobuf >= 3.6.0, < 3.8'
]

extras_require = {
  'grpc': ['grpcio>=1.2.0']
}

setuptools.setup(
  name='admobilizeapis',
  version='0.0.10',
  author='AdMobilize Team',
  author_email='devel@admobilize.com',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
  description='Protobufs used in AdMobilize Ecosystem',
  long_description='Protobuf message definition for AdMobilize services',
  install_requires=install_requires,
  extras_require=extras_require,
  license='GPLv3',
  namespace_packages=[
    'admobilize',
  ],
  packages=find_packages(),
  url='https://www.bitbucket.org/admobilize/admobilizeapis'
)
