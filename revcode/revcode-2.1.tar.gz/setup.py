import codecs
from setuptools import setup, find_packages

setup(
  name = 'revcode',
  packages = find_packages(),
  version = '2.1',
  description = 'A Roman encoding module for Indian languages',
  long_description = open('README.md').read(),
  author = 'Reverie Language Technologies',
  keywords = ['Roman Encoding', 'revcode', 'Indic languages', 'Indian languages'], 
  classifiers = [
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
  ],
)
