#! /usr/bin/python3

from setuptools import setup, find_packages

setup(name='kunny',
      version='0.1.1',
      license='MIT',
      author='kuner',
      packages= find_packages(),
      author_email='caohaowei99@gmail.com',
      description='A simple RPC framework',
      long_description=open('README.md').read(),
      install_requires=['msgpack>=0.6.1'],)
