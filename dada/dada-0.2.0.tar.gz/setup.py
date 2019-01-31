# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dada', 'dada.scripts']

package_data = \
{'': ['*'], 'dada': ['config/*']}

install_requires = \
['click>=7.0,<8.0', 'pick>=0.6.4,<0.7.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['dada = dada.scripts.dada:cli']}

setup_kwargs = {
    'name': 'dada',
    'version': '0.2.0',
    'description': 'Dada – a CLI project manager',
    'long_description': 'Dada\n==========\n\nDada is a CLI project manager – written in Python. It can be used\nfor switching quickly between projects and scaffolding them.\n\n\nInstalling\n----------\n\nInstall and update using pip:\n\n.. code-block:: text\n\n    $ pip install dada\n\nDada supports Python 3.7 and newer.\n\n\n\nCreating new projects\n---------------------\n\nTo create a new letter, type:\n\n.. code-block:: text\n\n    $ dada new letter\n\n\n\n\nLinks\n-----\n\n*   Website: https://palletsprojects.com/p/click/\n*   Documentation: https://click.palletsprojects.com/\n*   License: `BSD <https://github.com/pallets/click/blob/master/LICENSE.rst>`_\n*   Releases: https://pypi.org/project/click/\n*   Code: https://github.com/pallets/click\n*   Issue tracker: https://github.com/pallets/click/issues\n*   Test status:\n\n    *   Linux, Mac: https://travis-ci.org/pallets/click\n    *   Windows: https://ci.appveyor.com/project/pallets/click\n\n*   Test coverage: https://codecov.io/gh/pallets/click',
    'author': 'Dominic Looser',
    'author_email': 'dominic.looser@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
