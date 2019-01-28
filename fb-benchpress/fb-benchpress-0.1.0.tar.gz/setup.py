# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['benchpress',
 'benchpress.cli',
 'benchpress.cli.commands',
 'benchpress.lib',
 'benchpress.plugins',
 'benchpress.plugins.hooks',
 'benchpress.plugins.parsers']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses>=0.6.0,<0.7.0', 'pyyaml>=3.13,<4.0']

entry_points = \
{'console_scripts': ['benchpress = benchpress_cli:entry_point']}

setup_kwargs = {
    'name': 'fb-benchpress',
    'version': '0.1.0',
    'description': "Facebook kernel team's test runner",
    'long_description': None,
    'author': 'Vinnie Magro',
    'author_email': 'vmagro@fb.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
