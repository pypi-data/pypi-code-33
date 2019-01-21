# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['create_tomochain_masternode', 'create_tomochain_masternode.templates']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'jinja2>=2.10,<3.0']

entry_points = \
{'console_scripts': ['create-tomochain-masternode = '
                     'create_tomochain_masternode.main:entrypoint']}

setup_kwargs = {
    'name': 'create-tomochain-masternode',
    'version': '0.3.0b0',
    'description': 'Set up a TomoChain masternode by running one command.',
    'long_description': '# create-tomochain-masternode\nSet up a modern web app by running one command.\n',
    'author': 'etienne-napoleone',
    'author_email': 'etienne@tomochain.com',
    'url': 'https://tomochain.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
