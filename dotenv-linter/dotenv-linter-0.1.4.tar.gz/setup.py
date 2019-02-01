# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dotenv_linter',
 'dotenv_linter.grammar',
 'dotenv_linter.logics',
 'dotenv_linter.violations',
 'dotenv_linter.visitors',
 'dotenv_linter.visitors.fst']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.0,<7.0',
 'click_default_group>=1.2,<2.0',
 'ply>=3.11,<4.0',
 'typing_extensions>=3.6,<4.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

entry_points = \
{'console_scripts': ['dotenv-linter = dotenv_linter.cli:cli']}

setup_kwargs = {
    'name': 'dotenv-linter',
    'version': '0.1.4',
    'description': 'Linting dotenv files like a charm!',
    'long_description': '# dotenv-linter\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)\n[![Build Status](https://travis-ci.org/wemake-services/dotenv-linter.svg?branch=master)](https://travis-ci.org/wemake-services/dotenv-linter)\n[![Coverage](https://coveralls.io/repos/github/wemake-services/dotenv-linter/badge.svg?branch=master)](https://coveralls.io/github/wemake-services/dotenv-linter?branch=master)\n[![Python Version](https://img.shields.io/pypi/pyversions/dotenv-linter.svg)](https://pypi.org/project/dotenv-linter/)\n[![Documentation Status](https://readthedocs.org/projects/dotenv-linter/badge/?version=latest)](https://dotenv-linter.readthedocs.io/en/latest/?badge=latest)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/wemake-services/dotenv-linter/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n---\n\nSimple linter for `.env` files.\n\n![dotenv-logo](https://raw.githubusercontent.com/wemake-services/dotenv-linter/master/docs/_static/dotenv-logo@2.png)\n\nWhile `.env` files are very simple it is required to keep them consistent.\nThis tool offers a wide range of consistency rules and best practices.\n\nAnd it integrates perfectly to any existing workflow.\n\n\n## Installation\n\n```bash\npip install dotenv-linter\n```\n\nSee [Usage](https://dotenv-linter.readthedocs.io/en/latest/#usage)\nsection to get started.\n\n\n## Examples\n\nThere are many things that can go wrong in your `.env` files:\n\n```env\n# Next line has leading space which will be removed:\n SPACED=\n\n# Equal signs should not be spaced:\nKEY = VALUE\n\n# Quotes won\'t be preserved after parsing, do not use them:\nSECRET="my value"\n\n# Beware of duplicates!\nSECRET=Already defined ;(\n\n# Respect the convention, use `UPPER_CASE`:\nkebab-case-name=1\nsnake_case_name=2\n```\n\nAnd much more! You can find the [full list of violations in our docs](https://dotenv-linter.readthedocs.io/en/latest/pages/violations/).\n\n\n## Gratis\n\nSpecial thanks goes to [Ignacio Toledo](https://ign.uy)\nfor creating an awesome logo for the project.\n',
    'author': 'sobolevn',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://dotenv-linter.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
