# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['libtvdb', 'libtvdb.model']

package_data = \
{'': ['*']}

install_requires = \
['deserialize==0.7.0', 'keyper==0.3', 'requests==2.20.1']

setup_kwargs = {
    'name': 'libtvdb',
    'version': '0.3.0',
    'description': 'A wrapper around the TVDB API.',
    'long_description': '# libtvdb\n\nA wrapper around the [TVDB API](https://api.thetvdb.com/swagger).\n\n## Examples:\n\nSearching for shows:\n\n```\nimport libtvdb\nclient = libtvdb.TVDBClient(api_key="...", user_key="...", user_name="...")\nshows = client.search_show("Doctor Who")\n\nfor show in shows:\n    print(show.name)\n```\n\n## Advanced\n\nYou can set `libtvdb_api_key`, `libtvdb_user_key` and `libtvdb_user_name` in your OS X keychain if you don\'t want to supply these every time. If any of the values supplied to the `TVDBClient` constructor are `None`, it will look into your keychain and load the appropriate value. If it can\'t find them, it will throw an exception.\n',
    'author': 'Dale Myers',
    'author_email': 'dale@myers.io',
    'url': 'https://github.com/dalemyers/libtvdb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
