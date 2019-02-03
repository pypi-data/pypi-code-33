# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['falcon_epdb']

package_data = \
{'': ['*']}

install_requires = \
['epdb>=0.15.1,<0.16.0']

extras_require = \
{'fernet': ['cryptography>=2.5,<3.0'], 'jwt': ['PyJWT>=1.7,<2.0']}

setup_kwargs = {
    'name': 'falcon-epdb',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Josh Wilson',
    'author_email': 'josh.wilson@fivestars.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
