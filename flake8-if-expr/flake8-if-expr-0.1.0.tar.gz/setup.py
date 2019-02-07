# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flake8_if_expr']

package_data = \
{'': ['*']}

install_requires = \
['pycodestyle>=2.5,<3.0']

entry_points = \
{'flake8.extension': ['K100 = flake8_if_expr:IfExprChecker']}

setup_kwargs = {
    'name': 'flake8-if-expr',
    'version': '0.1.0',
    'description': '',
    'long_description': '# flake8-if-expr\n\n[![pypi](https://img.shields.io/badge/pypi-0.1.0-orange.svg)](https://pypi.org/project/flake8-if-expr)\n![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)\n![Downloads](https://img.shields.io/pypi/dm/flake8-if-expr.svg)\n[![Build Status](https://travis-ci.org/Afonasev/flake8-if-expr.svg?branch=master)](https://travis-ci.org/Afonasev/flake8-if-expr)\n[![Code coverage](https://codecov.io/gh/afonasev/flake8-if-expr/branch/master/graph/badge.svg)](https://codecov.io/gh/afonasev/flake8-if-expr)\n![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)\n![Code style: black](https://img.shields.io/badge/Style-Black-lightgrey.svg)\n\nCheck for if expression (ternary operator).\n\nThis module provides a plugin for flake8, the Python code checker.\n\n## Installation\n\n```bash\npip install flake8-if-expr\n```\n\n## Example\n\n```python\n# code.py\nx = 1 if 2 else 3\n```\n\n```bash\n$ flake8 code.py\n./code.py:1:5: K100 don`t use "[on_true] if [expression] else [on_false]" syntax\nx = 1 if 2 else 3\n    ^\n```\n\n## License\n\nMIT\n\n## Change Log\n\n### 0.1.0 - 2019.02.07\n\n* First release\n',
    'author': 'Afonasev Evgeniy',
    'author_email': 'ea.afonasev@gmail.com',
    'url': 'https://pypi.org/project/flake8-if-expr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
