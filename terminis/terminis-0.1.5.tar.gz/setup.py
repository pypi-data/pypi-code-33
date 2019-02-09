# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['terminis']

package_data = \
{'': ['*']}

extras_require = \
{':sys_platform == "Windows"': ['windows-curses>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['terminis = terminis.terminis:main']}

setup_kwargs = {
    'name': 'terminis',
    'version': '0.1.5',
    'description': 'Tetris clone for terminal. Ideal for servers without GUI!',
    'long_description': '# Terminis\nTetris clone for terminal. Ideal for servers without GUI!\n\n## Usage\n```bash\n  terminis [level]\n```\n  level: integer between 1 and 15\n',
    'author': 'adrienmalin',
    'author_email': '41926238+adrienmalin@users.noreply.github.com',
    'url': 'https://github.com/adrienmalin/Terminis',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
