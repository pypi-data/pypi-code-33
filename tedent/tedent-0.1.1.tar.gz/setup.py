# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tedent', 'tedent.fns', 'tedent.fns.decorators', 'tedent.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0', 'wrapt>=1.11,<2.0']

setup_kwargs = {
    'name': 'tedent',
    'version': '0.1.1',
    'description': 'like dedent but more flexible',
    'long_description': '# Tedent\n\nKeep your multi-line templated strings lookin\' good :sunglasses:\n\n*This is a python version of [tedent](https://github.com/olsonpm/tedent)*\n\n<br>\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [Tedent](#tedent)\n    - [What is it?](#what-is-it)\n    - [What does the name stand for?](#what-does-the-name-stand-for)\n    - [Why create it?](#why-create-it)\n    - [Simple Usage](#simple-usage)\n    - [Questions about how the indentation works?](#questions-about-how-the-indentation-works)\n    - [Important Usage Notes](#important-usage-notes)\n      - [input requirements](#edge-cases-and-input-requirements)\n    - [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### What is it?\n\n- A function similar to [dedent](https://docs.python.org/3.7/library/textwrap.html#textwrap.dedent)\n  just with different semantics\n\n<br>\n\n### What does the name stand for?\n\n- `Te`mplate string\n- in`dent`ation\n\nnames are hard\n\n<br>\n\n### Why create it?\n\n- dedent didn\'t handle the following case like I wanted\n\n```py\nformattedBoroughs = f"""\\\n[\n    \'Brooklyn\',\n    \'Manhattan\',\n]\n"""\n\nprint(\n    dedent(\n        f"""\\\n        New York boroughs\n        ${formattedBoroughs}\n        """\n    )\n)\n\n#\n# expected:\n# New York boroughs\n# [\n#     \'Brooklyn\',\n#     \'Manhattan\',\n# ]\n#\n# actual:\n#         New York boroughs\n#         [\n#     \'Brooklyn\',\n#     \'Manhattan\',\n# ]\n#\n```\n\n<br>\n\n### Simple Usage\n\n```py\nimport tedent from \'tedent\'\n\n#\n# *note the lack of the backslash\n#\nprint(\n    tedent(\n        """\n        This will be indented\n          as you expect\n        """\n    )\n)\n\n# writes:\n# This will be indented\n#   as you expect\n```\n\n<br>\n\n### Questions about how the indentation works?\n\nBecause the indentation logic is both young and convoluted, please refer to\n[the code](tedent/index.py) and [tests](tests/simple.py) for details. The\nlibrary is not that big and if you have any questions please create a\ngithub issue.\n\n<br>\n\n### Important Usage Notes\n\n- First of all, this library doesn\'t handle tabs. I will accept a PR\n  with support\n\n- Secondly, if you always use `tedent` like the following\n\n  ```py\n  tedent(\n      """\n      some text\n      """\n  )\n  ```\n\n  then you shouldn\'t run into any issues. However we all know input can be\n  tricky so `tedent` has a few input requirements in order to format your\n  string properly.\n\n#### input requirements\n\n- if the argument isn\'t a string then an error will be thrown\n- if you pass a string with three or more newlines, then\n  - the first and last lines must contain only whitespace\n  - the second line must contain a non-whitespace character\n  - _an error will be thrown if the above two conditions are not met_\n- if you pass a string with fewer than 3 newlines\n  - if they only contain whitespace then an empty string is returned\n  - otherwise an error is thrown\n- finally, all trailing whitespace from the result is stripped\n\nIf you have questions please raise a github issue.\n\n<br>\n\n### Test\n\n```py\n#\n# you must have poetry installed\n#\n$ poetry shell\n$ poetry install\n$ python runTests.py\n```\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_tedent',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
