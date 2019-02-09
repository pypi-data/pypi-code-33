# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flake8_return']

package_data = \
{'': ['*']}

entry_points = \
{u'flake8.extension': ['R50 = flake8_return:ReturnPlugin']}

setup_kwargs = {
    'name': 'flake8-return',
    'version': '0.1.0',
    'description': '',
    'long_description': '# flake8-return\n\n[![pypi](https://badge.fury.io/py/flake8-return.svg)](https://pypi.org/project/flake8-return)\n[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-return)\n[![Downloads](https://img.shields.io/pypi/dm/flake8-return.svg)](https://pypistats.org/packages/flake8-return)\n[![Build Status](https://travis-ci.org/Afonasev/flake8-return.svg?branch=master)](https://travis-ci.org/Afonasev/flake8-return)\n[![Code coverage](https://codecov.io/gh/afonasev/flake8-return/branch/master/graph/badge.svg)](https://codecov.io/gh/afonasev/flake8-return)\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\nFlake8 plugin that checks return values.\n\n## Installation\n\n```bash\npip install flake8-return\n```\n\n## Errors\n\n* R501 you shouldn\\`t add None at any return, if function havn\\`t return value except None\n* R502 you should add explicite value at every return, if function have not None return value\n* R503 you should add explicite return at end of the function, if function have not None return value\n\n## License\n\nMIT\n\n## Change Log\n\n### 0.1.0 - 2019.02.10\n\n* initial\n',
    'author': 'Afonasev Evgeniy',
    'author_email': 'ea.afonasev@gmail.com',
    'url': 'https://pypi.org/project/flake8-return',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
