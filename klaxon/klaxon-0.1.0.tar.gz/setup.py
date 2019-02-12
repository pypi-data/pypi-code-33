# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['klaxon']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['klaxon = klaxon:main']}

setup_kwargs = {
    'name': 'klaxon',
    'version': '0.1.0',
    'description': 'Use osascript to send notifications.',
    'long_description': None,
    'author': 'Stephan Fitzpatrick',
    'author_email': 'knowsuchagency@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
