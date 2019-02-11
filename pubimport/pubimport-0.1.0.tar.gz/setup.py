# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pubimport']

package_data = \
{'': ['*']}

install_requires = \
['bibtexparser>=1.1,<2.0', 'click>=7.0,<8.0', 'dominate>=2.3,<3.0']

entry_points = \
{'console_scripts': ['pubimport = pubimport:cli']}

setup_kwargs = {
    'name': 'pubimport',
    'version': '0.1.0',
    'description': '',
    'long_description': 'ksadfjkfj',
    'author': 'Dominic Looser',
    'author_email': 'dominic.looser@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
