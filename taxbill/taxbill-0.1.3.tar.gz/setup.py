# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['taxbill']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'pulp>=1.6,<2.0', 'pyyaml>=3.13,<4.0']

entry_points = \
{'console_scripts': ['taxbill = taxbill.cli:taxbill']}

setup_kwargs = {
    'name': 'taxbill',
    'version': '0.1.3',
    'description': 'Tax calculator and optimiser for UK freelancers',
    'long_description': None,
    'author': 'Owen Campbell',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
