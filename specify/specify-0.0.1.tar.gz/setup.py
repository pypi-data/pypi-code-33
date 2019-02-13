# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['specify']

package_data = \
{'': ['*']}

install_requires = \
['prophepy>=0.0.1']

setup_kwargs = {
    'name': 'specify',
    'version': '0.0.1',
    'description': 'A spec tool to describe your classes',
    'long_description': None,
    'author': 'Einenlum',
    'author_email': 'yann.rabiller@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
