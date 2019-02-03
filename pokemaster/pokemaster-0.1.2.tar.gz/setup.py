# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pokemaster']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0', 'construct==2.5.3', 'sqlalchemy>=1.2,<2.0']

setup_kwargs = {
    'name': 'pokemaster',
    'version': '0.1.2',
    'description': 'Get Real, Living™ Pokémon in Python',
    'long_description': "# `pokemaster` - Get Real, Living™ Pokémon in Python\n\n[![codecov](https://codecov.io/gh/kipyin/pokemaster/branch/develop/graph/badge.svg)](https://codecov.io/gh/kipyin/pokemaster) [![Travis CI](https://img.shields.io/travis/com/kipyin/pokemaster/develop.svg?label=Travis%20CI)](https://travis-ci.com/kipyin/pokemaster) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## What is this?\n\n`pokemaster` lets you create Pokémon\nthat is native to the core series Pokémon games\ndeveloped by Game Freak & Nintendo.\n\nIn `pokemaster`, \neverything you get is\nwhat you would expect in the games:\na Pokémon has a bunch of attributes,\nknows up to four moves,\ncan be evolved to another species,\ncan learn, forget, and remember certain moves,\ncan use moves to do stuff \n(such as attacking another Pokémon),\ncan consume certain items,\nand much, much more.\n\n## Installation\n\nInstall with `pip`:\n\n```shell\n$ pip install pokemaster\n```\n\n## Basic Usage\n\nTo summon a Real, Living™ Pokémon:\n\n```pydocstring\n>>> from pokemaster import Pokemon\n>>> bulbasaur = Pokemon(national_id=1, level=5)\n>>> eevee = Pokemon('eevee', level=10, gender='female')\n```\n\n",
    'author': 'Kip Yin',
    'author_email': 'kipyty@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'dependency_links': [
        'https://github.com/veekun/pokedex.git'
    ],
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
