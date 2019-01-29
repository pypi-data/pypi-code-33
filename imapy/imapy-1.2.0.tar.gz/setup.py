# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['imapy', 'imapy.packages']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'imapy',
    'version': '1.2.0',
    'description': 'Imapy: Imap for Humans',
    'long_description': None,
    'author': 'Vladimir Goncharov',
    'author_email': 'vladimarius@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7',
}


setup(**setup_kwargs)
