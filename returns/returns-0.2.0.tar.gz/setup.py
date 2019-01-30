# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['returns', 'returns.primitives']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'returns',
    'version': '0.2.0',
    'description': 'Monads for python made simple and safe.',
    'long_description': '# dry-monads\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services) [![Build Status](https://travis-ci.org/sobolevn/dry-monads.svg?branch=master)](https://travis-ci.org/sobolevn/dry-monads) [![Coverage Status](https://coveralls.io/repos/github/sobolevn/dry-monads/badge.svg?branch=master)](https://coveralls.io/github/sobolevn/dry-monads?branch=master) [![Documentation Status](https://readthedocs.org/projects/dry-monads/badge/?version=latest)](https://dry-monads.readthedocs.io/en/latest/?badge=latest) [![Python Version](https://img.shields.io/pypi/pyversions/dry-monads.svg)](https://pypi.org/project/dry-monads/) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n\nMonads for `python` made simple and safe.\n\n\n## Features\n\n- Provides primitives to write declarative business logic\n- Fully typed with annotations and checked with `mypy`,\n  allowing you to write type-safe code as well\n- No operator overloading or other unpythonic stuff that makes your eyes bleed\n\n\n## Installation\n\n\n```bash\npip install dry-monads\n```\n\n\n## What\'s inside?\n\nWe have several the most iconic monads inside:\n\n- [Result, Failure, and Success](https://dry-monads.readthedocs.io/en/latest/pages/either.html) (also known as `Either`, `Left`, and `Right`)\n- [Maybe, Some, and Nothing](https://dry-monads.readthedocs.io/en/latest/pages/maybe.html)\n\nWe also care about code readability and developer experience,\nso we have included some useful features to make your life easier:\n\n- [Do notation](https://dry-monads.readthedocs.io/en/latest/pages/do-notation.html)\n- [Helper functions](https://dry-monads.readthedocs.io/en/latest/pages/functions.html)\n\n\n## Example\n\n\n```python\nfrom returns.do_notation import do_notation\nfrom returns.either import Result, Success, Failure\n\nclass CreateAccountAndUser(object):\n    """Creates new Account-User pair."""\n\n    @do_notation\n    def __call__(self, username: str, email: str) -> Result[\'User\', str]:\n        """Can return a Success(user) or Failure(str_reason)."""\n        user_schema = self._validate_user(username, email).unwrap()\n        account = self._create_account(user_schema).unwrap()\n        return self._create_user(account)\n\n    # Protected methods\n    # ...\n\n```\n\nWe are [covering what\'s going on in this example](https://dry-monads.readthedocs.io/en/latest/pages/do-notation.html) in the docs.\n\n## Inspirations\n\nThis module is heavily based on:\n\n- [dry-rb/dry-monads](https://github.com/dry-rb/dry-monads)\n- [Ø](https://github.com/dbrattli/OSlash)\n- [pymonad](https://bitbucket.org/jason_delaat/pymonad)\n',
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://dry-monads.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
