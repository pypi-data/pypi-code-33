"""
Based on https://github.com/pypa/sampleproject
See https://github.com/pypa/sampleproject/blob/master/setup.py for explanations
"""

from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(
  name='skale-py',
  version='0.51.0',
  description='Skale client tools',

  long_description=long_description,
  #long_description_content_type='text/markdown',

  url='https://github.com/GalacticExchange/blockchain-node',
  author='Skale Labs',
  author_email='support@skalelabs.com',

  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Programming Language :: Python :: 3.6',
  ],

  packages=find_packages(exclude=['contrib', 'docs', 'tests']),
  install_requires=[
    'peppercorn',
    'web3',
    'asyncio',
    'PyYAML'
  ],

  include_package_data=True,
  package_data={  # Optional
    'contracts': ['utils/contracts_data.json', 'envs/envs.yml', 'envs/aws.json'],
  },
)
