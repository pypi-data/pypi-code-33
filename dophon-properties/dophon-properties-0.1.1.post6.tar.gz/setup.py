# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_properties',
 'dophon_properties.cloud',
 'dophon_properties.cloud.client',
 'dophon_properties.cloud.utils',
 'dophon_properties.database',
 'dophon_properties.dophon',
 'dophon_properties.mq',
 'dophon_properties.tools']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dophon-properties',
    'version': '0.1.1.post6',
    'description': 'dophon properties module',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
