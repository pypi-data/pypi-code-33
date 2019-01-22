# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fastest',
 'fastest.bodies',
 'fastest.code_assets',
 'fastest.compiler',
 'fastest.io',
 'fastest.type']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=10.0,<11.0', 'coverage>=4.5,<5.0', 'watchdog>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['fastest = fastest.__main__:main']}

setup_kwargs = {
    'name': 'fastest',
    'version': '0.0.12',
    'description': 'Automate tests via docstrings and more',
    'long_description': '# Fastest\nCreates unit tests from examples in the docstring and more.\n\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ae01d1185a9b4e93be06e6faf894448d)](https://app.codacy.com/app/AmreshVenugopal/fastest?utm_source=github.com&utm_medium=referral&utm_content=AmreshVenugopal/fastest&utm_campaign=Badge_Grade_Dashboard)\n[![Scrutinizer_Badge](https://scrutinizer-ci.com/g/AmreshVenugopal/fastest/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/AmreshVenugopal/fastest/)\n[![Coverage Status](https://coveralls.io/repos/github/AmreshVenugopal/fastest/badge.svg?branch=master)](https://coveralls.io/github/AmreshVenugopal/fastest?branch=master)\n[![Build_Status](https://travis-ci.org/AmreshVenugopal/fastest.svg?branch=master)](https://travis-ci.org/AmreshVenugopal/fastest)\n[![Current_Version](https://img.shields.io/pypi/v/fastest.svg)](https://pypi.org/project/fastest/)\n[![Python_Version](https://img.shields.io/pypi/pyversions/fastest.svg)](https://pypi.org/project/fastest/)\n\n## Install\n\n```bash\n$ pip install fastest\n```\n\n## Usage\n```bash\n$ fastest\n```\nwatches all .py files and creates coverage for entire project.\n\n```bash\n$ fastest --path=$(pwd) --source=py_module\n```\nwhere `path` is the the project root, and [`source`](https://coverage.readthedocs.io/en/coverage-4.3.4/source.html#source) \nis same as the value passed to the command `coverage run -m unittest --source=$source test`\n\n```bash\n$ fastest --exclude=dont_check_this_dir/*,these__*.py\n```\n\nTo exclude files/folders use `--exclude` and the file watcher will ignore them.\nThe `test/*` folder that `faster` creates is excluded by default.\n\n\n```bash\n$ fastest --poll-duration=10\n```\nBuilds files, runs tests and coverage every `10s`, default = `1s`\n\nThings that happen when you run `python main.py --path=$(pwd)`:\n\n 1. Checks for a `test` file at the project root, it creates if it doesn\'t find one.\n 2. Watches `.py` files for changes.\n 3. Creates unittests if a function has examples in its docstrings like so:\n\n```python\n# .\n# ├──module_a\n# ├──module_b\n#    └── utils.py\n#\ndef add(x, y):\n    """\n    ----\n    examples:\n    1) add(3, 4) -> 7\n    """\n    return x + y\n```\n\n This will create a unittest in the `test` directory, `assertEqual(add(3, 4), 7)`\n within `Class test_<file>_<function>(self)` \n (for the given directory, tree: `Class test_utils_add(self)`)\n\n 4. Runs all tests that are created.\n 5. Creates a coverage report (in html format).\n 6. Print the link to the coverage reports\' index.html.\n\n## How to make best use of Fastest\n 1. Keep your `functions` light:\n    - Be paranoid about separation of concerns.\n    - Too many conditions are a hint that you might need another function.\n    - Complex loops and `if-else` are not scalable code, a single mistake would \n    take that tower down and feature additions would involve someone going through \n    that brain-teaser.\n 2. Use libraries but wrap them with your own functions. Like: Use `requests` or the inevitable database? \n    wrap them with your own functions.\n    - Helps with adding customizations in one place (configuring things like base url, and similar configs)\n    - Helps mocking so that entire code-base can be unit tested.\n 3. Docstrings may get outdated if your work pace is fast enough to \n    maintain quality documentation, but adding examples now would help you create \n    tests which prevents your descriptions from going stale, **either the tests fail \n    AND the description is outdated OR else everything is fine**.\n\n\n## Examples:\n 1. Allows creation of variables within the docstrings, which includes lambda functions!\n     ```python\n    def quick_maths(a, b):\n        """\n        ----\n        examples:\n        @let \n        a = {\n            \'apples\': 3,\n            \'oranges\': 4\n        }\n        @end\n        \n        1) quick_maths(a[\'apples\'], a[\'oranges\']) -> 7\n        ----\n        """\n        return a + b\n     ```\n 2. You can run any valid python code within `@let--@end` blocks.\n 3. Can include installed modules external to your project.\n     ```python\n    def aint_nobody_got(time_fo_dat):\n        """\n        ---\n        examples:\n        @need\n        from datetime import datetime\n        @end\n        1) aint_nobody_got(time_fo_dat) -> datetime.now()\n        """\n     ```\n 4. If types are added to docstring, fastest will create tests\n for checking type of the value returned against empty of arguments.\n    ```python\n    def chain_strings(str1, str2):\n        """\n        :param str1: str\n        :param str2: str\n        :return: str\n        """\n        return str1 + str2\n    ``` \n    fastest will create a `assertInstanceIs(chain_strings(\'\', \'\'), str)` for the above snippet.\n',
    'author': 'AmreshVenugopal',
    'author_email': 'amresh.venugopal@gmail.com',
    'url': 'https://github.com/AmreshVenugopal/fastest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
