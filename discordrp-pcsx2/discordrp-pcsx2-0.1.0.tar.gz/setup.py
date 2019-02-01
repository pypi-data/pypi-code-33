# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['discordrp_pcsx2']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0', 'pypresence>=3.3,<4.0']

entry_points = \
{'console_scripts': ['discordrp-pcsx2 = discordrp_pcsx2:main']}

setup_kwargs = {
    'name': 'discordrp-pcsx2',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Discord Rich Presence for PCSX2\n\n## Installation: \n```bash\npip install discordrp-pcsx2\n```\n\n## Usage\n```bash\n$ discordrp-pcsx2 --help\nDiscord Rich Presence support for PCSX2.\n\nUsage:\n    discordrp_pcsx2 [--path=<path>]\n\nOptions:\n    --path=<path> Path to your PCSX2 directory, optional.\n```\n',
    'author': 'Jeremiah Boby',
    'author_email': 'mail@jeremiahboby.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
