# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cognitivecluster']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0',
 'scikit-learn>=0.20.2,<0.21.0',
 'tensorflow-hub>=0.2.0,<0.3.0',
 'tensorflow>=1.12,<2.0']

setup_kwargs = {
    'name': 'cognitivecluster',
    'version': '0.1.1',
    'description': 'A library to cluster partners based on metacognitive diversity',
    'long_description': None,
    'author': 'Michael Simpson',
    'author_email': 'michael@snthesis.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.7',
}


setup(**setup_kwargs)
