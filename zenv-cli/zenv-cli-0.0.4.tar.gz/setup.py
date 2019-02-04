# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['zenv']

package_data = \
{'': ['*']}

install_requires = \
['click', 'docker', 'toml>=0.9,<0.10']

entry_points = \
{'console_scripts': ['ze = zenv.cli:call', 'zenv = zenv.cli:cli']}

setup_kwargs = {
    'name': 'zenv-cli',
    'version': '0.0.4',
    'description': '',
    'long_description': 'Zenv: Zen Environment\n=====================\n\nZenv - docker based virtual environment for Developers!\n\nYou could execute any command inside container as in your native terminals\n\n',
    'author': 'evegny.zuev',
    'author_email': 'zueves@gmail.com',
    'url': 'https://github.com/zueve/zenv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
