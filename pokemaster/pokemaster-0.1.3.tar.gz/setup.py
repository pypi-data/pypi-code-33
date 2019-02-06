# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pokemaster']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0', 'sqlalchemy>=1.2,<2.0']

setup_kwargs = {
    'name': 'pokemaster',
    'version': '0.1.3',
    'description': 'Get Real, Living™ Pokémon in Python',
    'long_description': '# `pokemaster` - Get Real, Living™ Pokémon in Python\n\n[![codecov](https://codecov.io/gh/kipyin/pokemaster/branch/master/graph/badge.svg)](https://codecov.io/gh/kipyin/pokemaster) [![Travis CI](https://img.shields.io/travis/com/kipyin/pokemaster/master.svg?label=Travis%20CI)](https://travis-ci.com/kipyin/pokemaster) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## What is this?\n\n`pokemaster` lets you create Pokémon\nthat is native to the core series Pokémon games\ndeveloped by Game Freak & Nintendo.\n\nIn `pokemaster`, \neverything you get is\nwhat you would expect in the games:\na Pokémon has a bunch of attributes,\nknows up to four moves,\ncan be evolved to another species,\ncan learn, forget, and remember certain moves,\ncan use moves to do stuff \n(such as attacking another Pokémon),\ncan consume certain items,\nand much, much more.\n\n## Installation\n\n`pokemaster` can be installed via `pip`, but you have to have `pokedex`\ninstalled first:\n\n```shell\n$ pip install git+https://github.com/kipyin/pokedex\n$ pip install pokemaster\n```\n\n## Basic Usage\n\nTo summon a Real, Living™ Pokémon:\n\n```python\n>>> from pokemaster import Pokemon\n>>> bulbasaur = Pokemon(national_id=1, level=5)\n>>> eevee = Pokemon(\'eevee\', level=10, gender=\'female\')\n```\n\n## Development\n\n### Installing\n\nTo make contribution,\nyou need to clone the repo first, of course:\n\n```shell\n$ git clone https://github.com/kipyin/pokemaster.git\n$ cd pokemaster\n```\n\nIf you have `poetry` installed,\nyou can install the dependencies directly:\n\n```shell\n$ poetry install -v\n$ pip install git+https://github.com/kipyin/pokedex\n```\n\nIf you have `invoke` already,\nyou can install the dependencies with:\n\n```shell\n$ invoke install\n```\n\nThis command installs `poetry` and `pokedex`, \nand then runs `poetry install` for you.\n\nThis will equip everything you need for the development.\n\n### Linting\n\nWe use `black` to format the code,\nand `isort` to sort the imports.\n\nTo format the code,\nuse [invoke](http://docs.pyinvoke.org/en/stable/):\n\n```shell\n$ invoke lint\n```\n\n### Testing\n\nAfter making commits,\nmake sure all tests are passed.\nTo run tests, do\n\n```shell\n$ invoke test\n```\n\nIf you want to see the coverage:\n\n```shell\n$ invoke test-html\n```\n\n## LICENSE\n\nMIT License\n\nCopyright (c) 2019 Kip Yin\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'Kip Yin',
    'author_email': 'kipyty@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
