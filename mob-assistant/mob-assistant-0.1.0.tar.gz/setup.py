# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mob_assistant']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mob-assistant',
    'version': '0.1.0',
    'description': 'An assistant for mob programming.',
    'long_description': '# Mob Assistant\n[![Build Status](https://travis-ci.org/ddrexl/mob-assistant.svg?branch=master)](https://travis-ci.org/ddrexl/mob-assistant)\n',
    'author': 'Dominik Drexl',
    'author_email': 'domdrexl@gmail.com',
    'url': 'https://github.com/ddrexl/mob-assistant',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
