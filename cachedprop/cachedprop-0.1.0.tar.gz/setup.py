# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cachedprop']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=3.6,<4.0']

setup_kwargs = {
    'name': 'cachedprop',
    'version': '0.1.0',
    'description': 'cached property method decorator',
    'long_description': '# cachedprop\n[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)\n[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)\n[![Build Status](https://travis-ci.com/Spin14/cachedprop.svg?branch=master)](https://travis-ci.com/Spin14/cachedprop) \n\ncached property method decorator\n\n## Demo\n```python\nfrom cachedprop import cpd\n\n\nclass LabRat:\n    def __init__(self) -> None:\n        self._hp = None\n    \n    def expensive_hp_getter(self) -> int:\n        ...\n       \n    @cpd\n    def hp(self):\n        return self.expensive_hp_getter()\n        \n\nrat = LabRat()\nprint(rat.hp) # expensive_hp_getter is called, value gets "cached", prints value\nprint(rat.hp) # prints "cached" value only.\n```',
    'author': 'Joao Valverde',
    'author_email': 'acci.valverde@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
