# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['bonfig']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bonfig',
    'version': '0.2.1',
    'description': "Don't write configurations, write class declarations.",
    'long_description': '# Bonfig\n\n    from Bonfig import *\n    import configparser\n    class INIConfig(Bonfig):\n        store = Store()\n        SECTION = store.Section()\n        A = SECTION.FloatField()\n\n        def load(self):\n            self.store = configparser.ConfigParser()\n            self.store.read_string("[SECTION]\\nA = 3.14159")\n\nStop writing your configurations as dictionaries and strange floating dataclasses, make them `Bonfigs` and make use of\na whole bunch of great features:\n\n* Declare your configurations as easy to read classes.\n* Get all the power that comes with classes built into your configurations - polymorphism, custom methods and custom initialisation.\n* Sleep safe in the knowledge your config won\'t change unexpectedly.\n* Ready made serialisation and deserialisation with readmade custom `Fields` - `IntField`, `FloatField`, `BoolField` and `DatetimeField`.\n\n## Installation\n\n    pip install bonfig\n\nPlease checkout the project on github for more information: https://0hughman0.github.io/bonfig/index.html\n\n',
    'author': '0Hughman0',
    'author_email': 'rammers2@hotmail.co.uk',
    'url': 'https://github.com/0Hughman0/bonfig',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
