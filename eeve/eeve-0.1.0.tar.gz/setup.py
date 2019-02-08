# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['eeve']

package_data = \
{'': ['*'], 'eeve': ['eeve actions/*', 'eeve triggers/*']}

install_requires = \
['travel-backpack>=0.1.0']

setup_kwargs = {
    'name': 'eeve',
    'version': '0.1.0',
    'description': 'A flexible, powerfull and simple event trigger',
    'long_description': 'eeve\n====\n\n.. image:: https://img.shields.io/pypi/v/eeve.svg\n    :target: https://pypi.python.org/pypi/eeve\n    :alt: Latest PyPI version\n\n.. image::  .png\n   :target:  \n   :alt: Latest Travis CI build status\n\nA flexible, powerfull and simple event trigger\n\nUsage\n-----\n\nInstallation\n------------\n\nRequirements\n^^^^^^^^^^^^\n\nCompatibility\n-------------\n\nLicence\n-------\n\nAuthors\n-------\n\n`eeve` was written by `Victor Marcelino <victor.fmarcelino@gmail.com>`_.\n',
    'author': 'Victor Marcelino',
    'author_email': 'victor.fmarcelino@gmail.com',
    'url': 'https://github.com/vMarcelino/eeve',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
