# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tmn', 'tmn.elements']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'clint>=0.5.1,<0.6.0',
 'docker>=3.5.0,<4.0.0',
 'pastel>=0.1.0,<0.2.0',
 'python-slugify>=1.2,<2.0']

entry_points = \
{'console_scripts': ['tmn = tmn.tmn:main']}

setup_kwargs = {
    'name': 'tmn',
    'version': '0.5.0',
    'description': 'Quickstart your masternode',
    'long_description': '# tmn <a href="https://gitter.im/tomochain/tmn"><img align="right" src="https://badges.gitter.im/gitterHQ/gitter.png"></a>\n\n| Branch  | Status | Coverage |\n| --- | --- | --- |\n| Master | [![Build Status](https://travis-ci.org/tomochain/tmn.svg?branch=master)](https://travis-ci.org/tomochain/tmn) | [![Coverage Status](https://coveralls.io/repos/github/tomochain/tmn/badge.svg?branch=master)](https://coveralls.io/github/tomochain/tmn?branch=master) |\n| Develop | [![Build Status](https://travis-ci.org/tomochain/tmn.svg?branch=develop)](https://travis-ci.org/tomochain/tmn) | [![Coverage Status](https://coveralls.io/repos/github/tomochain/tmn/badge.svg?branch=develop)](https://coveralls.io/github/tomochain/tmn?branch=develop) |\n\nTomo MasterNode (tmn) is a cli tool to help you run a TomoChain masternode\n\n## Running and applying a masternode\n\nIf you are consulting this repo, it\'s probably because you want to run a masternode.\nFor complete guidelines on running a masternode candidate, please refer to the [documentation](https://docs.tomochain.com/masternode/requirements/).\n',
    'author': 'Etienne Napoleone',
    'author_email': 'etienne@tomochain.com',
    'url': 'https://tomochain.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
