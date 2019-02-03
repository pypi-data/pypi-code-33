# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['clubhouse']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.21,<3.0']

setup_kwargs = {
    'name': 'clubhouse',
    'version': '0.1.1',
    'description': 'Client for the Clubhouse API',
    'long_description': "# clubhouse-client\nPython client for Clubhouse\n\n## Usage\n\nRefer to [Clubhouse API Docs](https://clubhouse.io/api/rest/v2/) for more information.\n\n```python\nfrom clubhouse import ClubhouseClient\n\nclubhouse = ClubhouseClient('your api key')\n\nstory = {'name': 'A new story', 'description': 'Do something!'}\nclubhouse.post('stories', json=story)\n```\n",
    'author': 'Jean-Martin Archer',
    'author_email': 'jm@jmartin.ca',
    'url': 'https://github.com/j-martin/clubhouse-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
