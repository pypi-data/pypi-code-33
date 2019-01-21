# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['all_purpose_dict',
 'all_purpose_dict.fns',
 'all_purpose_dict.fns.decorators',
 'all_purpose_dict.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0', 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'all-purpose-dict',
    'version': '0.1.1',
    'description': 'A dict that works with both hashable and non-hashable keys',
    'long_description': '# All Purpose Dict\n\n*Note: This document is best viewed [on github](https://github.com/olsonpm/py_all-purpose-dict).\nPypi\'s headers are all caps which presents inaccurate information*"\n\n\n<br>\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [What is it?](#what-is-it)\n- [Why create it?](#why-create-it)\n- [Simple usage](#simple-usage)\n- [See Also](#see-also)\n- [Api](#api)\n  - [class ApDict([a list of pairs])](#class-apdicta-list-of-pairs)\n    - [clear()](#clear)\n    - [delete(key)](#deletekey)\n    - [get(key) => value](#getkey--value)\n    - [has(key) => bool](#haskey--bool)\n    - [keysIterator() => ApDictKeysIterator](#keysiterator--apdictkeysiterator)\n    - [set(key, value)](#setkey-value)\n    - [valuesIterator() => ApDictValuesIterator](#valuesiterator--apdictvaluesiterator)\n- [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### What is it?\n\n- A dict which doesn\'t require hashable keys\n\n<br>\n\n### Why create it?\n\n- I often have a need to store non-hashable keys in a dict.  For example storing\n  a dict as a key isn\'t possible with the builtin dict.\n\n  ```py\n  # doesn\'t work\n  someDict = { "key": "value" }\n  anotherDict = { someDict: "anotherValue" }\n  ```\n\n<br>\n\n### Simple usage\n\n```py\nfrom all_purpose_dict import ApDict\n\nsomeDict = { "key": "value" }\nanotherDict = ApDict([(someDict, "anotherValue")])\n\nprint(someDict in anotherDict) # prints True\n```\n\n<br>\n\n### See Also\n\n- [All Purpose Set](https://github.com/olsonpm/py_all-purpose-set)\n\n<br>\n\n### Api\n\n*Note: This api is young and subject to change quite a bit.  There also may be\nfunctionality present in the builtin dict which ApDict doesn\'t cover.  I\'m\nwilling to add it so please just raise a github issue or PR with details.*\n\n#### class ApDict([a list of pairs])\n- \'pairs\' may be either a list or tuple with a length of 2\n- all methods return `self` unless specified otherwise\n- iterates in the order of insertion\n- views are not implemented because I don\'t have a need for them. Instead I\n  expose `keysIterator` and `valuesIterator`.  If you need views then raise a\n  github issue.\n- the internal methods implemented are\n  - \\_\\_contains\\_\\_\n  - \\_\\_delitem\\_\\_\n  - \\_\\_getitem\\_\\_\n  - \\_\\_iter\\_\\_\n  - \\_\\_len\\_\\_\n  - \\_\\_setitem\\_\\_\n\n##### clear()\n\n##### delete(key)\n- a function alternative to `del aDict[key]`\n\n##### get(key) => value\n- a function alternative to `val = aDict[key]`\n\n##### has(key) => bool\n- a function alternative to `key in aDict`\n\n##### keysIterator() => ApDictKeysIterator\n\n##### set(key, value)\n- a function alternative to `aDict[key] = val`\n\n##### valuesIterator() => ApDictValuesIterator\n\n<br>\n\n### Test\n\n```sh\n#\n# you must have poetry installed\n#\n$ poetry shell\n$ poetry install\n$ python runTests.py\n```\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_all-purpose-dict',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
