# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pokemaster']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0', 'sqlalchemy>=1.2,<2.0']

extras_require = \
{'pokedex': ['pokedex', 'construct<=2.5.3']}

setup_kwargs = {
    'name': 'pokemaster',
    'version': '0.2.0',
    'description': 'Get Real, Living™ Pokémon in Python',
    'long_description': '# `pokemaster` - Get Real, Living™ Pokémon in Python\n\n[![Travis CI](https://img.shields.io/travis/com/kipyin/pokemaster/master.svg?label=Travis%20CI)](https://travis-ci.com/kipyin/pokemaster) [![codecov](https://codecov.io/gh/kipyin/pokemaster/branch/master/graph/badge.svg)](https://codecov.io/gh/kipyin/pokemaster) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/2ce3d3f469904b3a833c2a17045dff8a)](https://www.codacy.com/app/kipyin/pokemaster?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kipyin/pokemaster&amp;utm_campaign=Badge_Grade) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## Introduction\n\n`pokemaster` lets you create Pokémon\nthat is native to the core series Pokémon games\ndeveloped by Game Freak & Nintendo.\n\nIn `pokemaster`,\neverything you get is\nwhat you would expect in the games:\na Pokémon has a bunch of attributes,\nknows up to four moves,\ncan be evolved to another species,\ncan learn, forget, and remember certain moves,\ncan use moves to do stuff\n(such as attacking another Pokémon),\ncan consume certain items,\nand much, much more.\n\n## Installation\n\n`pokemaster` can be installed via `pip`, but you have to have `pokedex`\ninstalled first:\n\n```console\n$ pip install git+https://github.com/kipyin/pokedex\n$ pip install pokemaster\n```\n\nOr, if you have poetry, run:\n```console\n$ poetry add pokemaster -E pokedex\n```\n\n## Basic Usage\n\nTo summon a Real, Living™ Pokémon:\n\n```pycon\n>>> from pokemaster import Pokemon\n>>> bulbasaur = Pokemon(national_id=1, level=5)\n>>> eevee = Pokemon(\'eevee\', level=10, gender=\'female\')\n```\n\n## Development\n\n### Installing\n\nTo make contribution,\nyou need to clone the repo first, of course:\n\n```console\n$ git clone https://github.com/kipyin/pokemaster.git\n$ cd pokemaster\n```\n\nIf you have `poetry` installed,\nyou can install the dependencies directly:\n\n```console\n$ poetry install -v -E pokedex\n```\n\nThis will equip everything you need for the development.\n\n### Linting\n\nWe use `black` to format the code,\nand `isort` to sort the imports.\n\nThe best way to ensure all files are in the right format\nis using `tox`:\n\n```console\n$ tox -e lint\n```\n\n### Testing\n\nAfter making commits,\nmake sure all tests are passed.\nTo run tests against all environments,\nsimply do:\n\n```console\n$ tox\n```\n\nIf you want to run tests against specific Python version,\nuse `tox -e {env}`.\n\nFor example,\nif you want to run tests against Python 3.7,\nrun the following command:\n\n```console\n$ tox -e py37\n```\n\n## LICENSE\n\nMIT License\n\nCopyright (c) 2019 Kip Yin\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'Kip Yin',
    'author_email': 'kipyty@outlook.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
