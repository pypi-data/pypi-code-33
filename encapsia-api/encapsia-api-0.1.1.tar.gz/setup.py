# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['encapsia_api']

package_data = \
{'': ['*']}

install_requires = \
['requests[security]>=2.21,<3.0']

setup_kwargs = {
    'name': 'encapsia-api',
    'version': '0.1.1',
    'description': 'Client API for talking to an Encapsia system.',
    'long_description': '# Encapsia API Library\n\nREST API for working with Encapsia.\n\nSee https://www.encapsia.com.',
    'author': 'Timothy Corbett-Clark',
    'author_email': 'timothy.corbettclark@gmail.com',
    'url': 'https://github.com/tcorbettclark/encapsia-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
