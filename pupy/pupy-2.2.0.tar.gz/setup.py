# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['pupy']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'pupy',
    'version': '2.2.0',
    'description': 'pretty useful python',
    'long_description': None,
    'author': 'jessekrubin',
    'author_email': 'jessekrubin@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
