# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pymortar']

package_data = \
{'': ['*']}

install_requires = \
['googleapis-common-protos>=1.5,<2.0',
 'grpcio-tools>=1.18,<2.0',
 'grpcio>=1.18,<2.0',
 'pandas>=0.23.4,<0.24.0']

setup_kwargs = {
    'name': 'pymortar',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
