# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['terminis']

package_data = \
{'': ['*']}

extras_require = \
{':sys_platform == "win32"': ['windows-curses>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['terminis = terminis.terminis:main']}

setup_kwargs = {
    'name': 'terminis',
    'version': '0.1.11',
    'description': 'Tetris clone for terminal. Ideal for servers without GUI!',
    'long_description': '# Terminis\nTetris clone for terminal. Ideal for servers without GUI!\n\n## Installation\n\n```bash\npip install --user terminis\n```\n\n## Usage\n\n```bash\nterminis [edit|help|n]\n```\n* edit: edit controls in text editor\n* help: show command usage\n* n (integer between 1 and 15): start at level n\n',
    'author': 'adrienmalin',
    'author_email': '41926238+adrienmalin@users.noreply.github.com',
    'url': 'https://github.com/adrienmalin/Terminis',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7',
}


setup(**setup_kwargs)
