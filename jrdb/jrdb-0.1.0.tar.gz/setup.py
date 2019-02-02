# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrdb']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.3,<5.0', 'requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'jrdb',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'otomarukanta',
    'author_email': 'kanta208@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
