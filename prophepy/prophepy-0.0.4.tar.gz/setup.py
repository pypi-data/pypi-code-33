# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['prophepy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'prophepy',
    'version': '0.0.4',
    'description': 'Python mocks made for humans',
    'long_description': "# Prophepy\n\nPython mocks made for humans.\nHeavily inspired by the great PHP's [Prophecy](https://github.com/phpspec/prophecy).\n\n## Usage\n\n```python\nfrom examples.calculator import Calculator\nfrom examples.displayer import Displayer\nfrom prophepy import prophesize\n\ncalculator = prophesize(Calculator)\ndisplayer = Displayer(calculator._reveal())\n\ncalculator.add(2, 3)._should_be_called()\ncalculator.add(2, 3)._will_return(5)\ndisplayer.display_add(2, 3)\n\ncalculator.check_prophecies()\n```\n\n## Install\n\n`pip install prophepy`\n\n## Tests\n\n`python -m unittest tests/test.py`\n",
    'author': 'Einenlum',
    'author_email': 'yann.rabiller@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
