# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pokemaster']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0', 'construct==2.5.3', 'pokedex', 'sqlalchemy>=1.2,<2.0']

setup_kwargs = {
    'name': 'pokemaster',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Kip Yin',
    'author_email': 'kipyyin@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
