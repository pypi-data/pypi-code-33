# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['derivative']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0', 'scipy>=1.2,<2.0']

setup_kwargs = {
    'name': 'derivative',
    'version': '0.1.2',
    'description': '',
    'long_description': '`pip install derivative`\n',
    'author': 'Markus Quade',
    'author_email': 'info@markusqua.de',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
