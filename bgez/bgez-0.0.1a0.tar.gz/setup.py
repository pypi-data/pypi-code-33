# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bgez',
 'bgez.asyn',
 'bgez.components',
 'bgez.core',
 'bgez.core.inputs',
 'bgez.core.logging',
 'bgez.core.time',
 'bgez.core.utils',
 'bgez.game',
 'bgez.game.__api__',
 'bgez.game.inputs',
 'bgez.game.process',
 'bgez.game.types',
 'bgez.network',
 'bgez.network.multiplexer',
 'bgez.network.tcp',
 'bgez.network.udp',
 'bgez.stubs']

package_data = \
{'': ['*']}

install_requires = \
['promise>=2.2,<3.0', 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'bgez',
    'version': '0.0.1a0',
    'description': 'BGEz Framework for the Blender Game Engine',
    'long_description': None,
    'author': 'Paul Maréchal',
    'author_email': 'marechap.info@gmail.com',
    'url': 'https://gitlab.com/bgez/bgez',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
