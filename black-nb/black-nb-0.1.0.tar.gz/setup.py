# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

modules = \
['black_nb']
install_requires = \
['Click>=7.0,<8.0', 'black==18.9b0', 'nbformat>=4.4,<5.0']

entry_points = \
{'console_scripts': ['black-nb = black_nb:main']}

setup_kwargs = {
    'name': 'black-nb',
    'version': '0.1.0',
    'description': 'Apply black to all code cells in a Jupyter notebook.',
    'long_description': '<h1 align="center">black-nb :notebook: </h2>\n\n<p align="center">\n<a href="https://travis-ci.com/tomcatling/black-nb"><img alt="Build Status" src="https://travis-ci.com/tomcatling/black-nb.svg?branch=master"></a>\n<a href="https://codecov.io/github/tomcatling/black-nb?branch=master"><img alt="Code Coverage" src="https://codecov.io/github/tomcatling/black-nb/coverage.svg?branch=master"></a>\n<a href="https://github.com/ambv/black"><img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\n\n*black-nb* applies [*black*](https://github.com/ambv/black) to Jupyter notebooks.\n\nMuch of the code is taken from the original *black* project and the behaviour is intentionally similar.\n \n## Installation\n\n`pip install black-nb`\n\n## Usage\n\nTo apply *black* to all code cells in notebooks under the current directory:\n\n```bash\nblack-nb .\n```\nTo clear cell outputs in addition to reformatting:\n\n```bash\nblack-nb --clear-output .\n```\n\nTo check if notebooks pass *black* and additionally have no output (files will be unchanged):\n\n```bash\nblack-nb --clear-output --check .\n```\n\nTo reformat everything below `./` excluding `./outputs/*` and `*.ipynb_checkpoints/*` :\n\n```bash\nblack-nb --exclude /(outputs|\\.ipynb_checkpoints)/ .\n```\n\n## Command Line Options\n\n*black-nb* doesn\'t provide many options.  You can list them by running `black-nb --help`:\n\n```text\nblack-nb [OPTIONS] [SRC]...\n\nOptions:\n  -l, --line-length INTEGER   Where to wrap around.  [default: 88]\n                              \n  --check                     Don\'t write the files back, just return the\n                              status.  Return code 0 means nothing would\n                              change.  Return code 1 means some files would be\n                              reformatted.  Return code 123 means there was an\n                              internal error.\n                              \n  --include TEXT              A regular expression that matches files and\n                              directories that should be included on\n                              recursive searches. On Windows, use forward\n                              slashes for directories.  [default: \\.ipynb$]\n                              \n  --exclude TEXT              A regular expression that matches files and\n                              directories that should be excluded on\n                              recursive searches. On Windows, use forward\n                              slashes for directories.  [default:\n                              build/|buck-out/|dist/|_build/|\\.eggs/|\\.git/|\n                              \\.hg/|\\.mypy_cache/|\\.nox/|\\.tox/|\\.venv/|\\.ipynb_checkpoints]\n                              \n  --clear-output              Clearing code output is included in formatting.\n  \n  --help                      Show this message and exit.\n```\n\n\n## Copyright\n\nCopyright © 2019 Tom Catling.\n\n`black-nb` is distributed under the terms of the [ISC licence].\n\n[isc licence]: https://opensource.org/licenses/ISC\n',
    'author': 'Tom Catling',
    'author_email': 'tomcatling@gmail.com',
    'url': 'https://github.com/tomcatling/black-nb',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
