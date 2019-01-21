# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pretty_simple_namespace',
 'pretty_simple_namespace.fns',
 'pretty_simple_namespace.fns.decorators',
 'pretty_simple_namespace.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['all_purpose_dict>=0.1.2,<0.2.0',
 'all_purpose_set>=0.1.4,<0.2.0',
 'another_linked_list>=0.1.0,<0.2.0',
 'ordered_set>=3.1,<4.0',
 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'pretty-simple-namespace',
    'version': '0.1.0',
    'description': 'A pretty printer for SimpleNamespace',
    'long_description': '# Pretty SimpleNamespace\n\n*Note: This document is best viewed [on github](https://github.com/olsonpm/py_pretty-simple-namespace).\nPypi\'s headers are all caps which presents inaccurate information*\n\n\n<br>\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [What is it?](#what-is-it)\n- [Why create it?](#why-create-it)\n- [Simple usage](#simple-usage)\n- [Features](#features)\n- [Limitations](#limitations)\n- [Related projects](#related-projects)\n- [Api](#api)\n- [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### What is it?\n\n- A stringifier and formatter for SimpleNamespace which attempts to make the\n  data as readable as possible.\n\n<br>\n\n### Why create it?\n\n- I use SimpleNamespace often to hold state and needed a way to print it out for\n  debugging purposes.\n\n<br>\n\n### Simple usage\n\n```py\nfrom pretty_simple_namespace import pprint\nfrom types import SimpleNamespace as o\n\njoe = o(\n    name={"first": "joe", "last": "schmo"},\n    age=30,\n    favoriteFoods=["apples", "steak"],\n)\n\npprint(joe)\n# prints\n# {\n#   name: {\n#     first: \'joe\'\n#     last: \'schmo\'\n#   }\n#   age: 30\n#   favoriteFoods: [\n#     \'apples\'\n#     \'steak\'\n#   ]\n# }\n```\n\n<br>\n\n### Features\n- handles recursive structures by tracking and printing references nicely\n- recurses into types `list`, `dict` and `SimpleNamespace` for now\n- has special-case printing for types `bool`, `str`, `callable` and `None`\n  - booleans and None are printed lowercase\n  - strings are wrapped in single quotes\n  - callable appends `()` e.g. `myMethod()`.  Arguments aren\'t represented\n- all other types are printed by wrapping it in `str` e.g. `str(userDefinedType)`\n\n<br>\n\n### Limitations\n- multi-line strings look ugly\n- doesn\'t have a way to recurse into structures other than what\'s listed above\n\n<br>\n\n### Related projects\n\n- [tedent](https://github.com/olsonpm/py_tedent)\n\n<br>\n\n### Api\n\n#### format(something, indent=2) => str\n- formats `something` to a string as seen in [Simple usage](#simple-usage)\n\n#### pprint(something, indent=2) => None\n- just prints the formated `something`\n\n#### wrapWith(\\*, indent) => [Wrapped module](#wrapped-module)\n- use this when you want to call `format` or `pprint` with a different default\n  indent value so you don\'t have to pass it manually all the time.\n\n  e.g.\n  ```py\n  from pretty_simple_namespace import wrapWith\n\n  pprint = wrapWith(indent=4).pprint\n  pprint(o(tabbed4spaces=True))\n  # {\n  #     tabbed4spaces: true\n  # }\n  ```\n\n#### Wrapped module\n- just an instance of SimpleNamespace with two attributes `format` and `pprint`.\n\n<br>\n\n### Test\n\n```sh\n#\n# you must have poetry installed\n#\n$ poetry shell\n$ poetry install\n$ python runTests.py\n```\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_pretty-simple-namespace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
