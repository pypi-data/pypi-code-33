# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['python_nhc']

package_data = \
{'': ['*']}

install_requires = \
['nclib']

setup_kwargs = {
    'name': 'python-nhc',
    'version': '0.1.0',
    'description': 'Python controller for a Niko Home Control installation',
    'long_description': None,
    'author': 'gawood',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
