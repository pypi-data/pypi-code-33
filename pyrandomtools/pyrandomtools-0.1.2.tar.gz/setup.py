# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyrandomtools']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0']

setup_kwargs = {
    'name': 'pyrandomtools',
    'version': '0.1.2',
    'description': 'Random python functions organized into a module',
    'long_description': None,
    'author': 'Rick Alm',
    'author_email': 'rickealm@gmail.com',
    'url': 'http://github.com/rickalm/pyrandomtools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
