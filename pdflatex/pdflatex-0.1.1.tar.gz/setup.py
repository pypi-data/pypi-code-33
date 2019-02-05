# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pdflatex']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0']

setup_kwargs = {
    'name': 'pdflatex',
    'version': '0.1.1',
    'description': 'Simple wrapper to calling pdflatex',
    'long_description': None,
    'author': 'mbello',
    'author_email': 'mbello@users.noreply.github.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
