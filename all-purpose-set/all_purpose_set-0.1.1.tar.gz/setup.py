# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['all_purpose_set',
 'all_purpose_set.fns',
 'all_purpose_set.fns.decorators',
 'all_purpose_set.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0', 'tedent>=0.1.1,<0.2.0', 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'all-purpose-set',
    'version': '0.1.1',
    'description': 'A set that works with both hashable and non-hashable elements',
    'long_description': '# All Purpose Set\n\n*Note: This document is best viewed [on github](https://github.com/olsonpm/py_all-purpose-set).\nPypi\'s headers are all caps which presents inaccurate information*"\n\n\n<br>\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [What is it?](#what-is-it)\n- [Why create it?](#why-create-it)\n- [Simple usage](#simple-usage)\n- [Api](#api)\n  - [class ApSet([a list])](#class-apseta-list)\n    - [add(something)](#addsomething)\n    - [clear()](#clear)\n    - [has(something)](#hassomething)\n    - [remove(something)](#removesomething)\n- [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### What is it?\n\n- A set which doesn\'t require hashable contents\n\n<br>\n\n### Why create it?\n\n- I often have a need to store non-hashable contents in a set.  For example\n  storing a dict isn\'t possible with the builtin set.\n\n  ```py\n  # doesn\'t work\n  someDict = { "key": "value" }\n  someSet = { someDict }\n  ```\n\n<br>\n\n### Simple usage\n\n```py\nfrom all_purpose_set import ApSet\n\nsomeDict = { "key": "value" }\nsomeSet = ApSet([someDict])\n\nprint(someDict in someSet) # prints True\n```\n\n<br>\n\n### Api\n\n*Note: This api is young and subject to change quite a bit.  There also may be\nfunctionality present in the builtin set which this set doesn\'t cover.  I\'m\nwilling to add it so please just raise a github issue or PR with details.*\n\n#### class ApSet([a list])\n- all methods return `self` unless specified otherwise\n- iterates in the order of insertion\n- currently the internal methods implemented are\n  - \\_\\_contains\\_\\_\n  - \\_\\_iter\\_\\_\n  - \\_\\_len\\_\\_\n\n##### add(something)\n\n##### clear()\n\n##### has(something)\n- this is just for people who prefer the function syntax rather\n  than `key in aSet`\n\n##### remove(something)\n- raises a `KeyError` if the element doesn\'t exist\n\n<br>\n\n### Test\n\n```py\n#\n# you must have poetry installed\n#\n$ poetry shell\n$ poetry install\n$ python runTests.py\n```\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_all-purpose-set',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
