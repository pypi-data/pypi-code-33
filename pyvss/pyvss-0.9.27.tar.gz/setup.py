#!/usr/bin/env python
import pyvss
import os
import io

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def required():
    with io.open('requirements.txt', encoding='utf-8') as f:
        return f.read().splitlines()


def read(fname):
    with io.open(os.path.join(os.path.dirname(__file__), fname),
                 encoding='utf-8') as fo:
        return fo.read()


setup(name='pyvss',
      version=pyvss.__version__,
      description='ITS Private Cloud Python Client',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      author='University of Toronto - ITS',
      author_email='jm.lopez@utoronto.ca',
      maintainer='Virtualization & Storage Services',
      maintainer_email='vss-py@eis.utoronto.ca',
      url='https://eis.utoronto.ca/~vss/pyvss/',
      download_url='https://gitlab-ee.eis.utoronto.ca/vss/py-vss/tags',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      license='MIT License',
      packages=['pyvss'],
      platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix', 'OpenBSD'],
      install_requires=required()
      )
