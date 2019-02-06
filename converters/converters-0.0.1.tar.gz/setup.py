# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['converters']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'converters',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
