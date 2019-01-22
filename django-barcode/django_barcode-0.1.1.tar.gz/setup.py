# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_barcode']

package_data = \
{'': ['*'], 'django_barcode': ['templates/*']}

install_requires = \
['django>=2.1,<3.0', 'python-barcode>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'django-barcode',
    'version': '0.1.1',
    'description': 'A simple barcode field for Django models.',
    'long_description': None,
    'author': 'Andre Guerra',
    'author_email': 'andre.catarino.guerra@protonmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
