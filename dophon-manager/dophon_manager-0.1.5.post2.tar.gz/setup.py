# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_manager']

package_data = \
{'': ['*']}

install_requires = \
['poetry', 'toml']

entry_points = \
{'console_scripts': ['dophon = dophon_manager:main',
                     'dophon-manager = dophon_manager:main',
                     'dophon_manager = dophon_manager:main']}

setup_kwargs = {
    'name': 'dophon-manager',
    'version': '0.1.5.post2',
    'description': 'base manager for dophon framwork',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
