# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['carly']

package_data = \
{'': ['*']}

install_requires = \
['Twisted>=18.9,<19.0', 'attrs>=18.2,<19.0']

setup_kwargs = {
    'name': 'carly',
    'version': '0.9.1',
    'description': 'A tool for putting messages into and collecting responses from Twisted servers using real networking',
    'long_description': None,
    'author': 'Chris Withers',
    'author_email': 'chris@withers.org',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
