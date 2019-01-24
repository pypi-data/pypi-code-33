# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tid']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tid',
    'version': '0.2.0',
    'description': 'Get kernel thread id',
    'long_description': '# tid\n\nProvides an interface for getting the LWP id as visible in `ps`, `top`,\nand other utilities.\n\n```python\nimport tid\n\n\ntid.gettid()\n```\n\n# development\n\n```\npoetry install\npoetry build\npoetry publish\n```\n',
    'author': 'Chris Hunt',
    'author_email': 'chrahunt@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
