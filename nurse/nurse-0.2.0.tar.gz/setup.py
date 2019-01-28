# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nurse']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nurse',
    'version': '0.2.0',
    'description': 'A thoughtful dependency injection framework 💉',
    'long_description': None,
    'author': 'ducdetronquito',
    'author_email': 'g.paulet@zero-gachis.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
