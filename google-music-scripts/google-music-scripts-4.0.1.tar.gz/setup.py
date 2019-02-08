# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['google_music_scripts']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.0,<2.0',
 'audio-metadata>=0.4,<0.5',
 'google-music-proto>=2.4,<3.0',
 'google-music-utils>=2.1,<3.0',
 'google-music>=3.0,<4.0',
 'loguru>=0.2,<0.3',
 'natsort>=5.0,<7.0',
 'pendulum>=2.0,<3.0',
 'tomlkit>=0.5,<0.6']

extras_require = \
{'dev': ['flake8>=3.5,<4.0',
         'flake8-builtins>=1.0,<2.0',
         'flake8-import-order>=0.18,<0.19',
         'flake8-import-order-tbm>=1.0.0,<2.0.0',
         'sphinx>=1.7,<2.0',
         'sphinx-argparse>=0.2,<0.3'],
 'doc': ['sphinx>=1.7,<2.0', 'sphinx-argparse>=0.2,<0.3'],
 'lint': ['flake8>=3.5,<4.0',
          'flake8-builtins>=1.0,<2.0',
          'flake8-import-order>=0.18,<0.19',
          'flake8-import-order-tbm>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['gms = google_music_scripts.cli:run']}

setup_kwargs = {
    'name': 'google-music-scripts',
    'version': '4.0.1',
    'description': 'A CLI utility for interacting with Google Music.',
    'long_description': '# google-music-scripts\n\n[![PyPI](https://img.shields.io/pypi/v/google-music-scripts.svg?label=PyPI)](https://pypi.org/project/google-music-scripts/)\n![](https://img.shields.io/badge/Python-3.6%2B-blue.svg)  \n[![Docs - Stable](https://img.shields.io/readthedocs/google-music-scripts/stable.svg?label=Docs%20%28Stable%29)](https://google-music-scripts.readthedocs.io/en/stable/)\n[![Docs - Latest](https://img.shields.io/readthedocs/google-music-scripts/latest.svg?label=Docs%20%28Latest%29)](https://google-music-scripts.readthedocs.io/en/latest/)\n\n[google-music-scripts](https://github.com/thebigmunch/google-music-scripts)\nis a CLI utility for interacting with Google Music using my alternative to\ngmusicapi, [google-music](https://github.com/thebigmunch/google-music).\n\n\n## Installation\n\n``pip install - U google-music-scripts``\n\n\n## Usage\n\nFor the release version, see the [stable docs](https://google-music-scripts.readthedocs.io/en/stable/).  \nFor the development version, see the [latest docs](https://google-music-scripts.readthedocs.io/en/latest/).\n\n\n## Appreciation\n\nShowing appreciation is always welcome.\n\n#### Thank\n\n[![Say Thanks](https://img.shields.io/badge/thank-thebigmunch-blue.svg?style=flat-square)](https://saythanks.io/to/thebigmunch)\n\nGet your own thanks inbox at [SayThanks.io](https://saythanks.io/).\n\n#### Contribute\n\n[Contribute](https://github.com/thebigmunch/google-music-scripts/blob/master/.github/CONTRIBUTING.md) by submitting bug reports, feature requests, or code.\n\n#### Help Others/Stay Informed\n\n[Discourse forum](https://forum.thebigmunch.me/)\n\n#### Referrals/Donations\n\n[![Coinbase](https://img.shields.io/badge/Coinbase-referral-orange.svg?style=flat-square)](https://www.coinbase.com/join/52502f01e0fdd4d3ef000253) [![Digital Ocean](https://img.shields.io/badge/Digital_Ocean-referral-orange.svg?style=flat-square)](https://m.do.co/c/3823208a0597) [![Namecheap](https://img.shields.io/badge/Namecheap-referral-orange.svg?style=flat-square)](https://www.namecheap.com/?aff=67208) [![PayPal](https://img.shields.io/badge/PayPal-donate-brightgreen.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=DHDVLSYW8V8N4&lc=US&item_name=thebigmunch&currency_code=USD)\n\n**BTC:** ``1BMLCFPcX8YHE1He2t3aBrsNDGr1pKhfFa``  \n**ETH:** ``0x8E3f8d8eAedeA61Bf34A998A2104954FE508D5d0``  \n**LTC:** ``LgsQU1YaY4a4s7m9efjn6m35XhVEpW1xoP``\n',
    'author': 'thebigmunch',
    'author_email': 'mail@thebigmunch.me',
    'url': 'https://github.com/thebigmunch/google-music-scripts',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
