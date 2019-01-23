# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['epimetheus', 'epimetheus.exposers']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0', 'cached-property>=1.5,<2.0', 'sortedcontainers>=2.1,<3.0']

setup_kwargs = {
    'name': 'epimetheus',
    'version': '0.3.1',
    'description': 'Simplified prometheus client library',
    'long_description': None,
    'author': 'neumond',
    'author_email': 'knifeslaughter@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
