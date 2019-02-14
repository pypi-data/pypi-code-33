# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['grocer']
setup_kwargs = {
    'name': 'grocer',
    'version': '0.1.0',
    'description': 'Flat-file JSON store designed for concurrent write access',
    'long_description': None,
    'author': 'Barry Moore',
    'author_email': 'moore0557@gmail.com',
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
