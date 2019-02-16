# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dotup']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'crayons>=0.1.2,<0.2.0']

setup_kwargs = {
    'name': 'dotup',
    'version': '0.1.0',
    'description': 'Symlink your dotfiles with ease',
    'long_description': '# dotup\nSymlink your dotfiles with ease\n',
    'author': 'Ryan Castner',
    'author_email': 'castner.rr@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
