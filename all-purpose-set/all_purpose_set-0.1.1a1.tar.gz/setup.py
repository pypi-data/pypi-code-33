# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['all_purpose_set',
 'all_purpose_set.fns',
 'all_purpose_set.fns.decorators',
 'all_purpose_set.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0', 'tedent>=0.1.1,<0.2.0', 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'all-purpose-set',
    'version': '0.1.1a1',
    'description': 'A set that works with both hashable and non-hashable elements',
    'long_description': None,
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_all-purpose-set',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
