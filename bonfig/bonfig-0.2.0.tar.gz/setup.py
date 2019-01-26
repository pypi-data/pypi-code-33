# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bonfig']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bonfig',
    'version': '0.2.0',
    'description': "Don't write configurations, write class declarations.",
    'long_description': None,
    'author': '0Hughman0',
    'author_email': 'rammers2@hotmail.co.uk',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
