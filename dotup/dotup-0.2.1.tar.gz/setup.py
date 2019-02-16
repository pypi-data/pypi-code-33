# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dotup']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'crayons>=0.1.2,<0.2.0']

entry_points = \
{'console_scripts': ['dotup = dotup:dotup']}

setup_kwargs = {
    'name': 'dotup',
    'version': '0.2.1',
    'description': 'Symlink your dotfiles with ease.',
    'long_description': '<h3 align="center">\n  Dotup\n</h3>\n<h5 align="center">\n  <i>Symlink your dotfiles with ease.</i>\n</h5>\n\n---\n\nDotup will generate symlinks to your dotfiles and place them in your home directory through a convenient CLI.\n\n### Install\n\n```shell\n$ pip install dotup\n```\n\n### Usage\n\nBy default **dotup** expects to find a directory called `dotfiles` in your home directory `~/dotfiles`. Support for other dotfile directory paths is coming soon.\n\n```shell\n$ dotup\n```\n\nTo force symlink creation you can pass the `-f`, or `--force` flag.\n\n```shell\n$ dotup --force\n```\n\nHelp\n\n```shell\n$ dotup --help\n```\n\n### Development\n\nPull requests are welcome, please consider creating an issue first about the change you would like to make.\n\n### Deploy\n\nTo deploy a new version:\n\n1. Make a semantic version update to `dotup/__init__.py` and `pyproject.toml` files.\n2. Run `poetry-setup` see [poetry-setup](https://github.com/orsinium/poetry-setup) for installation\n3. Commit updated versions\n4. Run `poetry build`\n5. Run `poetry publish`\n',
    'author': 'Ryan Castner',
    'author_email': 'castner.rr@gmail.com',
    'url': 'https://github.com/audiolion/dotup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
