# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cleese']

package_data = \
{'': ['*']}

install_requires = \
['ampdup>=0.6.0,<0.7.0', 'carl>=0.0.7,<0.0.8']

entry_points = \
{'console_scripts': ['cleese = cleese.__main__:run_main']}

setup_kwargs = {
    'name': 'cleese-mpd',
    'version': '0.14.0',
    'description': 'An MPD client based on ampdup.',
    'long_description': None,
    'author': 'Tarcisio Eduardo Moreira Crocomo',
    'author_email': 'tarcisio.crocomo@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
