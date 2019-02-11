# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_mq',
 'dophon_mq.function_unit',
 'dophon_mq.local',
 'dophon_mq.properties',
 'dophon_mq.remote']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dophon-mq',
    'version': '1.0.0.post5',
    'description': 'dophon mq module',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
