# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dry_monads', 'dry_monads.primitives']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'dry-monads',
    'version': '0.1.0',
    'description': 'Monads for python made simple and safe.',
    'long_description': None,
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
