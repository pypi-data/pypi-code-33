#!/usr/bin/env python

from setuptools import setup
from os import path
import sys

# check that python version is 3.5 or above
python_version = sys.version_info
print('Running Python version %s.%s.%s' % python_version[:3])
if python_version < (3, 5):
    sys.exit('Python < 3.5 is not supported, aborting setup')
else:
    print('Confirmed Python version 3.5.0 or above')


def get_long_description():
    """ Finds the README and reads in the description """
    with open('README.md') as f:
            long_description = f.read()
    return long_description


version = '0.0.5'
long_description = get_long_description()

setup(name='ifomagic',
      description='',
      long_description=long_description,
      url='http://gitlab.sr.bham.ac.uk/ifolab/MAGIC/tree/master/Code',
      author='Isobel Romero-Shaw, Roshni Vincent, Andreas Freise',
      author_email='isobel.romeroshaw@gmail.com',
      version=version,
      packages=['magic', 'magic.detectors', 'magic.data', 'magic.optimisation',
                'magic.materials', 'magic.materials.suspension',
                'magic.materials.mirror', 'magic.noise', 'magic.noise.et',
                'magic.noise.ligo', 'magic.tools', 'magic.utils.filters',
                'magic.utils', 'magic.utils.et', 'magic.utils.ligo',
                'magic.utils.optics', 'magic.utils.power', 'magic.utils.transfer_functions'],
      package_data={'magic.data': ['ligo/*'],
                    'magic.optimisation': ['sourcesignals/*']},
      install_requires=[
          'pykat',
          'seaborn'],
      classifiers=[
          "Programming Language :: Python :: 3",
	  "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent"])
