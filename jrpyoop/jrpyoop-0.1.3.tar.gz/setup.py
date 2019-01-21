# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jrpyoop', 'jrpyoop.datasets']

package_data = \
{'': ['*'], 'jrpyoop': ['vignettes/*'], 'jrpyoop.datasets': ['data/*']}

install_requires = \
['pandas>=0.23.4,<0.24.0']

setup_kwargs = {
    'name': 'jrpyoop',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Colin',
    'author_email': 'colin@jumpingrivers.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
