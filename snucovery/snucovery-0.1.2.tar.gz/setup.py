# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['snucovery']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0', 'pyjq>=2.3,<3.0', 'xlsxwriter>=1.1,<2.0']

entry_points = \
{'console_scripts': ['pytest = scripts.pyt:py_test',
                     'snucovery = snucovery.__init__:main']}

setup_kwargs = {
    'name': 'snucovery',
    'version': '0.1.2',
    'description': 'Command Line utility to collect Aws Asset Data and export to Excel Stylesheets',
    'long_description': None,
    'author': 'Johnny Martin',
    'author_email': 'johnny.martin@tylertech.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
